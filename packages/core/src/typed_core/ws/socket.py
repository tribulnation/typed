from typing_extensions import Awaitable, TypeVar
from abc import ABC, abstractmethod
import asyncio
import contextlib
from dataclasses import dataclass, field
from datetime import timedelta
import logging
import websockets

from typed_core.exceptions import NetworkError

T = TypeVar('T')

logger = logging.getLogger(__name__)

@dataclass
class Context:
  ws: websockets.ClientConnection
  listener: asyncio.Task
  pinger: asyncio.Task

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
  """
  url: str
  timeout: timedelta = field(kw_only=True, default=timedelta(seconds=10))
  ping_interval: timedelta = field(kw_only=True, default=timedelta(hours=24))
  _ctx_future: 'asyncio.Future[Context] | None' = field(default=None, init=False, repr=False)
  """Backing store for `ctx_future`, `None` until something first reaches for it."""
  open_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  close_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

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

  @property
  async def ctx(self) -> Context:
    """The current connection context, opening one first if none exists yet.

    Reading this property is itself a connect-on-demand: it is right for any caller that
    wants to *use* the socket, but wrong for `__aexit__`, which must be able to close
    without ever opening.
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
    """
    if self._ctx_future is not None and self._ctx_future.done():
      await self.close(self._ctx_future.result(), exc_type, exc_value, traceback)
  
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
      try:
        return await websockets.connect(self.url, open_timeout=self.timeout.total_seconds())
      except websockets.exceptions.WebSocketException as e:
        raise NetworkError(f'Failed to connect to {self.url}') from e

    ws = await connect()
    logger.info('Connected!')
    return Context(
      ws=ws,
      listener=asyncio.create_task(self.listener(ws)),
      pinger=asyncio.create_task(self.pinger(ws)),
    )
  
  async def open(self):
    if self.open_lock.locked() or self.ctx_future.done():
      ctx = await self.ctx_future
      if ctx.ws.state == websockets.State.CLOSED:
        await self.close(ctx)
        return await self.open()
      else:
        return ctx

    async with self.open_lock:
      logger.info('Connecting...')
      ctx = await self.force_open()
      self.ctx_future.set_result(ctx)
      return ctx

  async def force_close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    ctx.listener.cancel()
    ctx.pinger.cancel()
    await ctx.ws.__aexit__(exc_type, exc_value, traceback)

  async def close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    if not self.close_lock.locked():
      async with self.close_lock:
        self._ctx_future = None
        await self.force_close(ctx, exc_type, exc_value, traceback)

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

    Args:
      fut: Future to wait for.
      ctx: Connection context to race against, if already held. Defaults to resolving
        `self.ctx` -- the only exception is a `force_open` override waiting on its own
        bootstrap reply, where `self.ctx` isn't resolved yet (it resolves through this
        same `force_open` call, still in progress) but the override already has the
        `Context` it just built, from `ctx = await super().force_open()` (see ADR 0005).
    """
    if ctx is None:
      ctx = await self.ctx
    async def coro():
      return await fut
    task = asyncio.create_task(coro())
    done, _ = await asyncio.wait([task, ctx.listener, ctx.pinger], return_when='FIRST_COMPLETED')
    if task not in done:
      # The listener/pinger won the race instead -- `task` is still pending
      # and nothing else will ever await or cancel it, so it would otherwise
      # be silently garbage-collected mid-flight ("Task was destroyed but it
      # is pending!").
      task.cancel()
      with contextlib.suppress(asyncio.CancelledError):
        await task
    if ctx.listener in done:
      if (exc := ctx.listener.exception()) is not None:
        raise exc
      else:
        raise RuntimeError('Listener task ended unexpectedly')
    elif ctx.pinger in done:
      if (exc := ctx.pinger.exception()) is not None:
        raise exc
      else:
        raise RuntimeError('Pinger task ended unexpectedly')
    return task.result()
