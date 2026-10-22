"""Gateway transport: one GRVT gateway (market data or trading) over HTTP and its WebSocket.

- HTTP: `{method} {base_url}{path}`, a JSON body for `POST`, query parameters for `GET`.
- WebSocket: the same RPC as JSON-RPC method `path` minus its `/full/` prefix.
- Both return the same body: `{"result": ...}` (plus `"next"` when paginated) for an RPC
  whose response struct has a `result` field, or that struct bare for any other RPC;
  unwrapped per `Meta.unwrap`.

The trading gateway carries a `Session` (cookie login, refreshed ahead of expiry and once
more when a call is answered `1000`), a `Signer` and a `Lookup` for EIP-712 payloads, and
fills a missing `sub_account_id` from the default trading sub-account (`Meta.sub_account`).
Its WebSocket authenticates with the session on the handshake (`GatewaySocket`).
"""

from dataclasses import dataclass, field, replace
from datetime import timedelta
from types import UnionType
import contextlib
import json

from typing_extensions import Any, Awaitable, Callable, TypeVar, cast

from typed_core.exceptions import (
  AuthError,
  BadRequest,
  LogicError,
  NetworkError,
  ValidationError,
)
from typed_core.http import HttpClient
from typed_core.util import Stream, StreamManager

from ..auth import Session, SessionState
from ..endpoint.gateway import GatewayClient, Meta, Sign, SubAccount, Transport
from ..envelope import UNAUTHENTICATED, check_gateway, unwrap
from ..lookup import Lookup
from ..owners import Connection, Owned
from ..signing import Signer
from ..wire import dump, fill, load, normalize_channel
from .ws import FeedFrame, GatewaySocket, Unauthenticated

T = TypeVar('T')
R = TypeVar('R')

FULL_PREFIX = '/full/'
"""HTTP path prefix of a full-encoding RPC; the rest of the path is its JSON-RPC method."""


def unsigned(payload: Any) -> bool:
  """Whether a wire payload still needs its signature (none, or one without `r`)."""
  signature = payload.get('signature') if isinstance(payload, dict) else None
  return not isinstance(signature, dict) or not signature.get('r')


def unauthenticated(error: AuthError) -> bool:
  """Whether `error` is the venue's `1000`: no (valid) session, so the call was never
  processed and is safe to retry after logging in again."""
  return bool(error.args) and error.args[0] == UNAUTHENTICATED


@dataclass(kw_only=True)
class GatewayTransport(Owned, GatewayClient):
  """One GRVT gateway: HTTP RPCs, JSON-RPC over WebSocket, and stream subscriptions.

  Its `HttpClient` and socket close when its last owner leaves (`Owned`). The market-data
  gateway is also owned by the trading gateway whose `lookup` reads from it, so it counts
  both; the trading gateway takes one ownership of the session and of that lookup in turn.
  So `async with client.trading` alone closes everything it opened, including the
  market-data connection signing read instrument and currency facts over, while an `async
  with client.market` still open keeps that one open.
  """

  base_url: str
  """HTTP base URL, e.g. `https://trades.grvt.io`."""
  socket: GatewaySocket
  """The gateway's JSON-RPC WebSocket."""
  http: HttpClient = field(default_factory=HttpClient)
  session: Session | None = None
  """Session for authenticated calls; `None` for the public market-data gateway."""
  authenticated: bool = False
  """Every call needs `session` (the trading gateway)."""
  signer: Signer | None = None
  """Signs EIP-712 payloads; `None` when no private key was given."""
  lookup: Lookup | None = None
  """Instrument and currency facts signing needs."""
  signature_ttl: timedelta = timedelta(days=1)
  """Lifetime of a generated signature (the venue caps it at 30 days). For a
  `GOOD_TILL_TIME` order it is also the order's expiry."""
  trading_account_id: str | None = None
  """Configured default trading sub-account id (`{prefix}TRADING_ACCOUNT_ID`), if any."""
  trading_account_var: str | None = None
  """Environment variable `trading_account_id` was read from, named in errors; `None` when
  the credentials were passed as arguments, since nothing is read from the environment
  then."""
  validate: bool = True

  def connections(self) -> list[Connection]:
    """The gateway's HTTP pool and socket, closed when its last owner leaves."""
    return [self.http, self.socket]

  def shared(self) -> list[Owned]:
    """What this transport shares with others and owns once more while owned itself: the
    session, and the lookup (which owns the market-data gateway it reads from)."""
    return [x for x in (self.session, self.lookup) if x is not None]

  def should_validate(self, validate: bool | None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  def require_session(self):
    """Refuse an authenticated gateway's call up front when there is no session.

    Raises:
      AuthError: This is the trading gateway of a client built with `public=True`.
    """
    if self.authenticated and self.session is None:
      raise AuthError('No credentials: this client was built with `public=True`')

  async def sub_account_id(self) -> str:
    """The default trading sub-account: `trading_account_id` when configured, else the one
    the session's API key is scoped to (logging in first if needed).

    Raises:
      AuthError: A public client (built with `public=True`), or a session scoped to no
        sub-account (a funding-account key or a wallet login) with no configured
        `trading_account_id`. The error says how to configure one: the environment
        variable when the credentials came from the environment, else `trading_account_id`.
    """
    if self.trading_account_id:
      return self.trading_account_id
    self.require_session()
    if self.session is not None and (
      sub := (await self.session.state()).sub_account_id
    ):
      return sub
    if self.trading_account_var:
      configure = f'Set {self.trading_account_var} or pass trading_account_id to new()'
    else:
      configure = 'Pass trading_account_id to new() along with the keys'
    raise AuthError(
      'No default trading sub-account: the session is not scoped to one (a funding-account '
      f'API key, or a wallet login). {configure}, pass sub_account_id to the call, or log '
      'in with a trading-account API key'
    )

  async def fill_sub_account(self, where: SubAccount, wire: Any) -> Any:
    """Fill a missing (or `None`) `sub_account_id` with the default trading sub-account.

    For `orders`, the request's own top-level `sub_account_id` is filled as well as each
    order's: the venue requires it (`1001` without it, verified live on `v2/bulk_orders`).

    Args:
      where: Where the request carries it (`Meta.sub_account`).
      wire: The request (or stream parameters), before serialization; returned as is when
        every slot is already set, else as a filled copy (the caller's value is never
        modified).

    Raises:
      AuthError: A slot needs the default and none is available.
      LogicError: The request (or the payload `where` names) is not a JSON object.
    """
    wire = {} if wire is None else wire
    if not isinstance(wire, dict):
      raise LogicError(
        f'Cannot fill sub_account_id into a non-object request: {wire!r}'
      )
    if where == 'request':
      slots: list[Any] = [wire]
    elif where == 'order':
      slots = [wire.get('order')]
    else:
      slots = [wire, *(wire.get('orders') or [])]
    if not all(isinstance(p, dict) for p in slots):
      raise LogicError(f'Cannot fill sub_account_id into {where!r} of {wire!r}')
    payloads = cast(list[dict[str, Any]], slots)
    if all(p.get('sub_account_id') is not None for p in payloads):
      return wire
    sub = await self.sub_account_id()
    filled = [
      p if p.get('sub_account_id') is not None else {**p, 'sub_account_id': sub}
      for p in payloads
    ]
    if where == 'request':
      return filled[0]
    if where == 'order':
      return {**wire, 'order': filled[0]}
    top, *orders = filled
    return {**top, 'orders': orders} if 'orders' in wire else top

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: Meta | None = None,
    validate: bool | None = None,
    transport: Transport = 'http',
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Call one RPC; see `GatewayEndpoint.request` for the arguments.

    The default sub-account is filled in before the request is serialized and checked
    against `request_type`, so a `sub_account_id` left out or `None` is never sent as such.

    Raises:
      AuthError: No session for an authenticated gateway, the venue rejected it twice, or a
        `sub_account_id` to fill has no default.
      BadRequest: The request does not match `request_type` (see `wire.dump`).
      LogicError: `transport='ws'` on a path with no JSON-RPC method.
    """
    self.require_session()
    meta = meta or {}
    if (where := meta.get('sub_account')) is not None:
      request = await self.fill_sub_account(where, request)
    wire = dump(request, request_type, operation=path)
    if (sign := meta.get('sign')) is not None:
      wire = await self.sign(sign, wire)
    if transport == 'ws':
      body = await self.ws_call(path, wire)
    else:
      body = await self.http_call(method=method or 'POST', path=path, wire=wire)
    payload = unwrap(body, meta.get('unwrap', 'result'))
    return load(payload, response_type, validate=self.should_validate(validate))

  async def http_call(self, *, method: str, path: str, wire: Any) -> Any:
    """Send one HTTP call, logging in again once if the venue reports an expired session.

    A body-carrying call with no request sends `{}`: the venue rejects an empty `POST` body
    with `1003` (verified live on `/full/v1/currency`).
    """
    url = self.base_url + path
    content = (
      None
      if method == 'GET'
      else json.dumps(wire if wire is not None else {}, separators=(',', ':'))
    )
    params = wire if method == 'GET' else None
    for attempt in (1, 2):
      state = await self.session.state() if self.session is not None else None
      response = await self.http.request(
        method,
        url,
        content=content,
        params=params,
        headers={
          'Content-Type': 'application/json',
          **(state.headers if state is not None else {}),
        },
      )
      try:
        return check_gateway(response)
      except AuthError as e:
        if not self.retry_login(e, state, attempt):
          raise
    raise LogicError('unreachable')

  def retry_login(
    self, error: AuthError, state: SessionState | None, attempt: int
  ) -> bool:
    """Whether to retry a call after `error`: once, when an existing session was rejected
    with `1000`, which means the call was never processed."""
    if self.session is None or state is None or attempt > 1:
      return False
    if not unauthenticated(error):
      return False
    self.session.invalidate(state)
    return True

  async def ws_call(self, path: str, wire: Any) -> Any:
    """Send one RPC as JSON-RPC over the gateway socket, reconnecting with a fresh session
    once if the venue answers `1000` (the call was never processed).

    Every call answered `1000` retries on its own, including concurrent calls on the same
    rejected connection; they share one re-login, and the connection is closed only after
    the replies pending on it have landed (`GatewaySocket.retire`). Live subscriptions on it
    then end with `NetworkError` and must be resubscribed. A `NetworkError` is never
    retried: the call may have been processed.

    Raises:
      LogicError: `path` is not a full-encoding RPC path.
    """
    if not path.startswith(FULL_PREFIX):
      raise LogicError(f'{path} has no JSON-RPC method; it is only reachable over HTTP')
    method = path.removeprefix(FULL_PREFIX)
    return await self.retry_rejected(lambda: self.socket.call(method, wire or {}))

  async def retry_rejected(self, attempt: Callable[[], Awaitable[T]]) -> T:
    """Run one WS call, retrying it once after the venue answered it `1000`.

    A call refused unsent (its connection was already rejected) is retried without counting
    as the attempt: it never reached the venue.

    Raises:
      AuthError: The venue answered `1000` again on the fresh connection.
    """
    sent = 0
    while True:
      try:
        return await attempt()
      except Unauthenticated as e:
        sent += e.sent
        rejected = e
      if sent > 1:
        # Raised outside the handler: the caller gets a plain `AuthError`, never the
        # internal `Unauthenticated` carrying the dead connection.
        raise AuthError(*rejected.args) from rejected.__cause__
      await self.socket.retire(rejected.ctx)

  async def sign(self, sign: Sign, wire: Any) -> Any:
    """Fill in the EIP-712 signature of the payload `sign` names, when still unsigned.

    For `order`/`orders` the payloads are the orders themselves, so a request carrying
    none (a bulk cancel by ids) goes out as it came, unsigned. For every other kind the
    payload is the request.

    Raises:
      AuthError: There is no signer (no private key was given).
      BadRequest: A position request names no instrument.
      LogicError: The request is not a JSON object, or there is no market-data lookup to
        sign with.
    """
    if not isinstance(wire, dict):
      raise LogicError(f'Cannot sign a non-object request: {wire!r}')
    if sign == 'order':
      orders = [wire['order']] if 'order' in wire else []
    elif sign == 'orders':
      orders = list(wire.get('orders') or [])
    else:
      orders = []
    if sign in ('order', 'orders'):
      # Only the orders are signed: a request without any (a bulk cancel) is sent unsigned
      # and unchanged, and needs no private key.
      if not any(unsigned(o) for o in orders):
        return wire
    elif not unsigned(wire):
      return wire
    if self.signer is None:
      raise AuthError(
        'No private key: this request must be signed; pass private_key to Grvt.new()'
      )
    if self.lookup is None:
      raise LogicError('No market-data lookup to sign with')
    signer, ttl = self.signer, self.signature_ttl
    if sign == 'derisk':
      return signer.derisk(wire, ttl=ttl)
    if sign in ('position_config', 'position_margin'):
      name = wire.get('instrument')
      if not isinstance(name, str):
        raise BadRequest(f'instrument must be an instrument name, got {name!r}')
      instrument = (await self.lookup.instrument_keys({name}))[name]
      if sign == 'position_config':
        return signer.position_config(wire, instrument, ttl=ttl)
      quote = await self.lookup.currency_key(instrument['quote'])
      return signer.position_margin(wire, instrument, quote, ttl=ttl)
    if sign in ('transfer', 'withdrawal'):
      currency = await self.lookup.currency_key(wire['currency'])
      if sign == 'transfer':
        return signer.transfer(wire, currency, ttl=ttl)
      return signer.withdrawal(wire, currency, ttl=ttl)
    names = {leg['instrument'] for order in orders for leg in order.get('legs', [])}
    keys = await self.lookup.instrument_keys(names)
    signed = [signer.order(o, keys, ttl=ttl) if unsigned(o) else o for o in orders]
    if sign == 'order':
      return {**wire, 'order': signed[0]}
    return {**wire, 'orders': signed}

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: Meta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
    reply_type: type[R] | UnionType | None = None,
  ) -> StreamManager[T, R, Any]:
    """Subscribe one selector; see `GatewayEndpoint.subscribe` for the arguments.

    Each yielded item is a frame's `feed`. A repeated delta is dropped, a gap or decrease
    in `sequence_number` ends the stream with `NetworkError` (the venue's own rule:
    resubscribe), and a frame without an integer one ends it with `ValidationError`. The
    first delta must be the reply's `first_sequence_number`, so one lost right after the
    snapshot is caught too (verified live on 8 market-data streams and on `v1.order`).

    Whatever ends a stream after the venue subscribed it (a malformed reply, a sequence
    break, a feed failing validation) unsubscribes it before raising, for `await` and
    `async with` callers alike, so the same selector can be subscribed again right away.

    Every whole `0x` address in the filled selector is lowercased, whether it came from a
    placeholder or was written into `channel` already: the venue matches address selectors
    case-sensitively against the lowercase form and answers a checksummed one with `1001`
    (verified live on `v1.deposit` and `v1.withdrawal`). A missing `sub_account_id` is
    filled when `meta.sub_account` says so. A subscribe answered `1000` reconnects with a
    fresh session and subscribes once more, like every other call on that rejected
    connection, ending its other streams (see `ws_call`).

    Raises:
      AuthError: No session for an authenticated gateway (raised on subscribing), or a
        `sub_account_id` to fill has no default.
      BadRequest: The parameters do not match `request_type` (see `wire.dump`), or the
        same channel is already subscribed.
    """
    meta = meta or {}
    should_validate = self.should_validate(validate)

    async def connect() -> Stream[T, R, Any]:
      """Subscribe, then validate the reply and map every frame to its checked feed."""
      self.require_session()
      values = parameters
      if (where := meta.get('sub_account')) is not None:
        values = await self.fill_sub_account(where, values)
      name = channel.partition(':')[0]
      wire = dump(values, request_type, operation=f'stream {name}') or {}
      key, extra = fill(channel, wire)
      key = normalize_channel(key)
      stream = await self.open_stream(key, extra)
      try:
        sequence = Sequence(key, last=seed(stream.reply))
        reply = load(stream.reply, reply_type, validate=should_validate)
      except Exception:
        await release(stream)
        raise

      async def feeds():
        """Yield each new frame's validated feed, releasing the subscription if it breaks."""
        try:
          async for frame in stream.stream:
            if sequence.accept(frame):
              yield load(frame['feed'], response_type, validate=should_validate)
        except Exception:
          await release(stream)
          raise

      return replace(cast(Stream[Any, Any, Any], stream), reply=reply, stream=feeds())

    return StreamManager(connect=connect)

  async def open_stream(
    self, key: str, extra: dict[str, Any]
  ) -> Stream[FeedFrame, Any, Any]:
    """Subscribe one `{stream}:{selector}` key, reconnecting with a fresh session once if
    the venue answers `1000` (see `ws_call`).

    Args:
      key: The filled channel key.
      extra: Extra subscribe params.

    Raises:
      BadRequest: `key` is already subscribed on the live connection.
    """
    try:
      return await self.retry_rejected(
        lambda: self.socket.subscribe(key, extra or None).connect()
      )
    except RuntimeError:
      # typed_core refuses a second subscription to a live channel with a bare
      # RuntimeError; the socket's own subscriptions say whether that is what happened.
      if key in self.socket.subscriptions:
        raise BadRequest(
          f'Already subscribed to {key!r}: reuse that stream, or unsubscribe it first'
        ) from None
      raise


def seed(reply: Any) -> int | None:
  """The number before the first delta a subscribe reply announces, if it announces one.

  One selector per subscribe, so `first_sequence_number[0]` is this subscription's. It is
  read off the raw reply, since validation may reshape it. A reply announcing none
  (`v1.cancel` answers empty lists) leaves the subscription unseeded.

  Raises:
    ValidationError: The announced number is not an integer.
  """
  firsts = reply.get('first_sequence_number') if isinstance(reply, dict) else None
  if not firsts:
    return None
  try:
    return int(firsts[0]) - 1
  except (TypeError, ValueError, KeyError):
    raise ValidationError(
      f'Subscribe reply with a non-integer first_sequence_number: {firsts!r}'
    ) from None


async def release(stream: Stream[Any, Any, Any]):
  """Unsubscribe a stream that broke, so the failure that broke it is what gets raised.

  An unsubscribe that fails too (the connection dropped, or no reply came) is ignored:
  the subscription is forgotten locally all the same, so whatever the venue still pushes
  for it is dropped, and the selector can be subscribed again.
  """
  with contextlib.suppress(Exception):
    await stream.unsubscribe()


@dataclass
class Sequence:
  """Per-subscription `sequence_number` bookkeeping.

  Only the initial snapshot frames carry `sequence_number` `"0"`. Every later frame
  (including those on `.s` snapshot streams) carries a counter that is per stream and
  selector and per gateway instance: it continues across connections and resets on a
  gateway restart. The subscribe reply's `first_sequence_number` (`latest + 1`) is the first
  delta to expect, so `last` is seeded with `first - 1`; unseeded (`v1.cancel`, whose reply
  lists nothing), the first delta that arrives is taken as is.

  A repeat of the last number is a duplicate (dropped); a decrease or a skipped number means
  the stream is no longer consistent (reconnect). Every feed frame the venue sends carries a
  `sequence_number`, so a frame without one, or with a non-integer one, is malformed rather
  than a snapshot: it raises instead of bypassing the check.
  """

  key: str
  last: int | None = None
  """The last delivered delta's number, or the seed (`first_sequence_number - 1`)."""

  def accept(self, frame: FeedFrame) -> bool:
    """Whether to deliver `frame`.

    Raises:
      NetworkError: A delta's number decreased or skipped one or more numbers.
      ValidationError: The frame has no `sequence_number`, or one that is not an integer.
    """
    raw: Any = frame.get('sequence_number')
    try:
      number = int(raw)
    except (TypeError, ValueError):
      raise ValidationError(
        f'{self.key}: feed frame with no integer sequence_number: {raw!r}'
      ) from None
    if number == 0:
      return True
    if self.last is not None:
      if number == self.last:
        return False
      if number != self.last + 1:
        kind = 'decrease' if number < self.last else 'gap'
        raise NetworkError(
          f'{self.key}: sequence {kind}, {self.last} -> {number}; resubscribe'
        )
    self.last = number
    return True
