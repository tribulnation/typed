"""Bybit v5 WebSocket connections, mirroring `bybit.http` for HTTP.

Bybit's v5 WebSocket surface is nine separate connections, not one — see
`bybit.core.ws` for why. `Http` needs only `base_url`/`http`/`credentials` and builds
`market`/`account` itself via `Router`'s reflection; `Ws` plays the same role here, but
plainly rather than reflectively — see `Ws.new` — since there is no comparable
mechanism for a class whose children each own a distinct socket instead of sharing one
pool.
"""

from typing_extensions import Self
from dataclasses import dataclass

from typed_bybit.core.auth import Credentials
from typed_bybit.core.ws import BybitStreamsClient, BybitTradeClient, WsUrls
from .finance import FinanceChannels
from .private import Private
from .public.inverse import InverseChannels
from .public.linear import LinearChannels
from .public.option import OptionChannels
from .public.spot import SpotChannels
from .rfq import Rfq
from .spread import SpreadChannels
from .trade import Trade


@dataclass(kw_only=True)
class Ws:
  """Every Bybit v5 WebSocket connection, reachable from the one client root.

  A plain container — every field is a required constructor argument, so a test can
  build one with a hand-picked child (a mock socket, a fake URL) without going through
  `new`. `new` is the thin, transport-local constructor: it takes already-resolved
  `urls` and `credentials` rather than resolving region/testnet/environment itself —
  `Bybit.new` (`bybit.main`) owns that once, for this and `Http.new` alike. One
  `Credentials | None` flows to every connection that can use it: the seven public
  category/offer streams never authenticate regardless, `private` refuses to open without it,
  and `trade` refuses to build a signed frame without it. Each connection is already
  lazy-open and partial-close on its own (`typed_core.ws.Socket`), so nothing here dials
  out until a caller actually subscribes or sends a command.
  """

  credentials: Credentials | None
  spot: SpotChannels
  linear: LinearChannels
  inverse: InverseChannels
  option: OptionChannels
  spread: SpreadChannels
  rfq: Rfq
  private: Private
  trade: Trade
  finance: FinanceChannels
  """Advanced Earn's fixed-price offer channels (`finance.advanced_earn.websocket.*_offer`),
  on their own connection (`WsUrls.fp`) -- public, no auth handshake."""

  @classmethod
  def new(cls, *, urls: WsUrls, credentials: Credentials | None = None) -> Self:
    """Build every connection against an already-resolved set of URLs.

    Args:
      urls: One URL per connection — see `bybit.core.ws.resolve_ws_urls`.
      credentials: Shared by `private` and `trade`; the six public streams ignore it.
    """
    return cls(
      credentials=credentials,
      spot=SpotChannels(socket=BybitStreamsClient(url=urls['spot'])),
      linear=LinearChannels(socket=BybitStreamsClient(url=urls['linear'])),
      inverse=InverseChannels(socket=BybitStreamsClient(url=urls['inverse'])),
      option=OptionChannels(socket=BybitStreamsClient(url=urls['option'])),
      spread=SpreadChannels(socket=BybitStreamsClient(url=urls['spread'])),
      rfq=Rfq(socket=BybitStreamsClient(url=urls['rfq'])),
      private=Private(
        socket=BybitStreamsClient(
          url=urls['private'],
          credentials=credentials,
          require_auth=True,
        )
      ),
      trade=Trade(socket=BybitTradeClient(url=urls['trade'], credentials=credentials)),
      finance=FinanceChannels(socket=BybitStreamsClient(url=urls['fp'])),
    )

  def _sockets(self):
    return (
      self.spot.socket,
      self.linear.socket,
      self.inverse.socket,
      self.option.socket,
      self.spread.socket,
      self.rfq.socket,
      self.private.socket,
      self.trade.socket,
      self.finance.socket,
    )

  async def __aenter__(self):
    for socket in self._sockets():
      await socket.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    for socket in self._sockets():
      await socket.__aexit__(exc_type, exc_value, traceback)
