from typing_extensions import Awaitable, TypeVar
from abc import ABC, abstractmethod
import asyncio
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import timedelta
import inspect
import logging
import websockets

from typed_core.exceptions import NetworkError

T = TypeVar('T')

logger = logging.getLogger(__name__)

@dataclass
class Context:
  """One connection and the background tasks serving it."""
  ws: websockets.ClientConnection
  listener: asyncio.Task
  pinger: asyncio.Task
  closed: bool = False
  """Set once `Socket.close` has started closing this connection."""

  @property
  def alive(self) -> bool:
    """Whether this connection can still carry work: open, served and not being closed."""
    return (
      not self.closed and not self.listener.done() and not self.pinger.done()
      and self.ws.state is websockets.State.OPEN
    )

  def failure(self) -> BaseException:
    """The error to raise for work bound to this connection once it is no longer alive."""
    for task, name in ((self.listener, 'Listener'), (self.pinger, 'Pinger')):
      if task.done():
        if task.cancelled():
          return NetworkError('WebSocket connection closed')
        if (exc := task.exception()) is not None:
          return exc
        return RuntimeError(f'{name} task ended unexpectedly')
    return NetworkError('WebSocket connection closed')

BOUND: 'ContextVar[tuple[Socket, Context] | None]' = ContextVar('typed_core.ws.bound', default=None)
"""The socket and connection that the work started by `Socket.wait` runs on.

Inside that work, resolving `Socket.ctx` (or `Socket.ws`) returns this connection, or
raises once it is gone: work bound to a connection never opens a new one.
"""

def fail_replies(replies: 'dict[int, asyncio.Future]'):
  """Fail and forget every pending reply of a connection being closed."""
  for reply in replies.values():
    if not reply.done():
      reply.set_exception(NetworkError('WebSocket connection closed'))
      reply.exception() # retrieved by its waiter, if any; never logged as unretrieved
  replies.clear()

class ClosedByOwner(NetworkError):
  """The owner exited while this connect was in flight, so its connection was closed."""

def close_coroutine(fut: Awaitable):
  """Close `fut` if it is a coroutine that will never be awaited, so it doesn't warn."""
  if inspect.iscoroutine(fut):
    fut.close()

@dataclass
class Socket(ABC):
  """Base WebSocket client.
  
  ### Features
  - Connection handling
  - Optional periodic pinging
  - Message listener
  - Error propagation via `.wait(...)`

  ### Requires implementing
  - `on_msg`: handle incoming messages.
  - `ping`: if you the server requires some custom pinging mechanism

  ### Concurrency Contract
  1. Connection: single owner via `async with`, also supports lazy no-owner use
  2. Requests: many concurrent `wait()` calls OK

  ### Error Propagation

  The websocket connection could fail without you knowing.
  To avoid that happening, you can ensure they are propagated by using `.wait(...)`.

  **Example**:

  ```python
  future = asyncio.Future()

  class MySocket(Socket):
    def on_msg(self, msg: str | bytes):
      future.set_result(msg)

  async with MySocket('wss://example.com') as ws:
    result = await ws.wait(future)
  ```

  If you awaited directly and an exception happened, you would wait forever.
  
  This way, if an error happens, a `NetworkError` will be raised.

  ### Dropped Connections

  Work is bound to the connection it started on. When that connection drops or is
  closed, the work in `.wait(...)` on it raises `NetworkError` and never moves to a new
  connection. New work reconnects transparently.

  ### Exiting While Connecting

  The owner's exit never waits for a connect in flight. It counts itself in `exits`, and a
  connect that started before it closes its own connection once it completes, failing
  with `NetworkError` for every caller that joined it before the exit. A caller that
  joined it only after the exit tries once more, on a fresh connection.
  """
  url: str
  timeout: timedelta = field(kw_only=True, default=timedelta(seconds=10))
  ping_interval: timedelta = field(kw_only=True, default=timedelta(hours=24))
  _ctx_future: 'asyncio.Future[Context] | None' = field(default=None, init=False, repr=False)
  """Backing store for `ctx_future`, `None` until something first reaches for it."""
  open_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  close_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  """Unused: kept for compatibility. Closing is idempotent per connection (`Context.closed`)."""
  exits: int = field(default=0, init=False, repr=False)
  """How many times the owner has exited; a connect that saw it move closes what it opened."""

  @property
  def ctx_future(self) -> 'asyncio.Future[Context]':
    """Future holding the connection once one is opened, created on first access.

    Deliberately not a `default_factory`: `asyncio.Future()` binds the running loop as it
    is constructed, so a socket built outside a loop -- a client constructed in a
    synchronous test fixture, or at module scope -- raised `RuntimeError` before anything
    had a chance to connect. A client that owns a socket it may never use has to be
    constructible anywhere; the loop is needed when the socket opens, not when it is built.
    """
    if self._ctx_future is None:
      self._ctx_future = asyncio.Future()
    return self._ctx_future

  @abstractmethod
  def on_msg(self, msg: str | bytes):
    ...

  async def ping(self, ws: websockets.ClientConnection):
    """Ping the server.

    If implemented, this is called periodically by the pinger task.

    Args:
      ws: The live connection, handed directly rather than resolved via `self.ws` —
        `pinger` runs from the moment `force_open` creates it, before `self.ctx` has
        anything to resolve to.
    """
    raise NotImplementedError

  async def pinger(self, ws: websockets.ClientConnection):
    while True:
      await asyncio.sleep(self.ping_interval.total_seconds())
      try:
        await self.ping(ws)
      except NotImplementedError:
        ...
      except websockets.exceptions.WebSocketException as e:
        raise NetworkError('Error sending ping') from e

  @property
  async def ctx(self) -> Context:
    """The current connection context, opening one first if none exists yet.

    Reading this property is itself a connect-on-demand: it is right for any caller that
    wants to *use* the socket, but wrong for `__aexit__`, which must be able to close
    without ever opening. Inside work started by `wait(...)`, it is that work's own
    connection instead (see `open`).
    """
    return await self.open()

  @property
  async def ws(self) -> websockets.ClientConnection:
    return (await self.ctx).ws

  async def __aenter__(self):
    """Take ownership without connecting; the socket opens lazily on first use."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection if one was opened; do nothing when none ever was.

    Deliberately not `await self.ctx` -- that property falls through to `open()`, so a
    client that only ever used the other transport would dial out here just to hang up.

    Never waits for a connect in flight, which may be stuck in a handshake: counting the
    exit in `exits`, before any await, is what makes that connect close its own
    connection when it completes (see `open`).
    """
    self.exits += 1
    future = self._ctx_future
    if future is None or not future.done() or future.cancelled() or future.exception() is not None:
      return
    await self.close(future.result(), exc_type, exc_value, traceback)
  
  async def force_open(self):
    """Connect, then hand the live connection straight to `listener`/`pinger`.

    Deliberately not `self.listener()`/`self.pinger()` resolving `ws` themselves via
    `self.ws` — that property goes through `self.ctx` -> `self.open()`, which is *this
    call*, still in progress. A subclass override that needs to send-and-await a reply
    during its own `force_open` (an auth handshake, say) would otherwise deadlock: the
    listener can't start delivering until `self.ctx_future` resolves, and it only
    resolves once `force_open` returns — which it can't, waiting on a reply only the
    listener can deliver. Passing `ws` as a parameter here means `listener`/`pinger`
    never need `self.ctx` at all, so there's nothing left for them to wait on.
    """
    async def connect():
      # `websockets.connect` raises `OSError` for a refused or unreachable host (DNS,
      # TCP, TLS), `TimeoutError` when the handshake outlives `open_timeout`, and
      # `EOFError` when the peer closes mid-handshake -- none of them
      # `WebSocketException`s, so catching only that let the most common failure, a
      # refused connection, escape as a raw `OSError` a caller's `except NetworkError`
      # never saw.
      try:
        return await websockets.connect(self.url, open_timeout=self.timeout.total_seconds())
      except (websockets.exceptions.WebSocketException, OSError, EOFError, TimeoutError) as e:
        raise NetworkError(f'Failed to connect to {self.url}') from e

    ws = await connect()
    logger.info('Connected!')
    return Context(
      ws=ws,
      listener=asyncio.create_task(self.listener(ws)),
      pinger=asyncio.create_task(self.pinger(ws)),
    )
  
  async def open(self):
    """The live connection, connecting first if there is none or the last one is gone.

    Inside work started by `wait(...)`, returns that work's own connection and never
    opens a new one.

    Raises:
      NetworkError: Connecting failed, the bound connection is gone, or the owner exited
        while the connect this call joined was in flight.
    """
    return await self._open(self.exits)

  async def _open(self, exits: int, *, retried: bool = False) -> Context:
    """`open`, for a caller that started when the owner had exited `exits` times.

    Every connection this call opens, or reopens after finding the current one dead,
    is closed again rather than returned if the owner exits meanwhile.
    """
    bound = BOUND.get()
    if bound is not None and bound[0] is self:
      ctx = bound[1]
      if not ctx.alive:
        raise ctx.failure()
      return ctx

    if self.open_lock.locked() or self.ctx_future.done():
      # Shielded: the future is shared with the connecting task and every other waiter,
      # so cancelling this caller must not cancel it.
      try:
        ctx = await asyncio.shield(self.ctx_future)
      except ClosedByOwner:
        # The connect started before an exit. A caller that started after it doesn't
        # belong to the owner that left: it tries once more, on a fresh connection.
        if retried or self.exits != exits:
          raise
        return await self._open(exits, retried=True)
      if ctx.alive:
        return ctx
      await self.close(ctx)
      if self.exits != exits:
        raise ClosedByOwner('WebSocket closed by its owner')
      return await self._open(exits, retried=retried)

    async with self.open_lock:
      logger.info('Connecting...')
      future = self.ctx_future
      try:
        ctx = await self.force_open()
      except BaseException as e:
        # Callers waiting on this attempt share its failure instead of waiting forever;
        # the next call starts a fresh attempt.
        if self._ctx_future is future:
          self._ctx_future = None
        if not future.done():
          future.set_exception(e if isinstance(e, Exception) else NetworkError('Connecting was cancelled'))
          future.exception() # nobody may be waiting on it; never logged as unretrieved
        raise
      if not future.done() and self.exits == exits:
        future.set_result(ctx)
        return ctx
      # Cancelled by someone else, or the owner exited, while connecting: nobody may
      # receive this connection.
      if self._ctx_future is future:
        self._ctx_future = None
      if future.done():
        error: NetworkError = NetworkError('Connecting was cancelled')
      else:
        error = ClosedByOwner('WebSocket closed by its owner while connecting')
        future.set_exception(error)
        future.exception() # nobody may be waiting on it; never logged as unretrieved
    # Closed outside the lock: a held lock means a connect in flight, and a caller retrying
    # now must start its own rather than wait on one that will never resolve.
    await self.close(ctx)
    raise error

  def connection_closed(self, ctx: Context):
    """Forget the state bound to a connection being closed.

    Called by `close` before the connection goes down, whether it dropped or the owner is
    closing it. Override to fail or discard per-connection state, calling `super()`.
    """
    if (parent := getattr(super(), 'connection_closed', None)) is not None:
      parent(ctx)

  async def force_close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    ctx.listener.cancel()
    ctx.pinger.cancel()
    await ctx.ws.__aexit__(exc_type, exc_value, traceback)

  async def close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    """Close `ctx` once, detaching it first so new work opens a fresh connection.

    Cancelled during the close handshake, it aborts the connection before re-raising.
    """
    if ctx.closed:
      return
    ctx.closed = True
    future = self._ctx_future
    if future is not None and future.done() and future.result() is ctx:
      self._ctx_future = None
    self.connection_closed(ctx)
    for task in (ctx.listener, ctx.pinger):
      if task.done() and not task.cancelled():
        task.exception() # a drop is reported through the work bound to it, not logged here
    try:
      await self.force_close(ctx, exc_type, exc_value, traceback)
    except asyncio.CancelledError:
      # Cancelled mid close handshake: drop the TCP connection instead of leaving it
      # half-closed, since the connection is already detached and nothing can reach it.
      ctx.ws.transport.abort()
      raise

  async def listener(self, ws: websockets.ClientConnection):
    while True:
      try:
        msg = await ws.recv()
        logger.debug('Received: %s', msg)
        self.on_msg(msg)
      except websockets.exceptions.WebSocketException as e:
        logger.error('Error receiving message: %s', e)
        raise NetworkError('Error receiving message') from e

  async def wait(self, fut: Awaitable[T], *, ctx: Context | None = None) -> T:
    """Wait for a future to complete, propagating any exceptions in the background tasks.

    `fut` runs bound to `ctx`: resolving `self.ctx`/`self.ws` inside it returns `ctx`, and
    never opens a new connection once `ctx` is gone. A coroutine that never gets to run is
    closed, not left unawaited.

    Args:
      fut: Future to wait for.
      ctx: Connection context to race against, if already held. Defaults to resolving
        `self.ctx` -- the only exception is a `force_open` override waiting on its own
        bootstrap reply, where `self.ctx` isn't resolved yet (it resolves through this
        same `force_open` call, still in progress) but the override already has the
        `Context` it just built, from `ctx = await super().force_open()`.

    Raises:
      NetworkError: The connection dropped or was closed before `fut` completed.
    """
    try:
      if ctx is None:
        ctx = await self.ctx
      if not ctx.alive:
        raise ctx.failure()
    except BaseException:
      close_coroutine(fut)
      raise

    token = BOUND.set((self, ctx))
    try:
      if inspect.iscoroutine(fut):
        task = asyncio.ensure_future(fut)
      else:
        async def forward():
          """Await `fut` from a task this wait owns."""
          return await fut
        task = asyncio.ensure_future(forward())
    finally:
      BOUND.reset(token)

    try:
      done, _ = await asyncio.wait(
        [task, ctx.listener, ctx.pinger], return_when='FIRST_COMPLETED'
      )
    finally:
      # The request task belongs to this wait, including when its caller is
      # cancelled. The shared listener/pinger belong to the socket, not this call.
      task.cancel()
      await asyncio.gather(task, return_exceptions=True)
    if ctx.listener in done or ctx.pinger in done:
      raise ctx.failure()
    return task.result()
