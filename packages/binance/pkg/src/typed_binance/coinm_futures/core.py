"""COIN-M Futures' own resolved core (`codegen/config.toml` `[python.cores.coinm_futures]`,
design §5c): composes REST, market streams, the private user-data stream, and the WS
API, each holding its own already-built transport client forwarded from
`core.base.CoinMFuturesClients`.
"""

from typing_extensions import Self
from dataclasses import dataclass

from ..core.base import CoinMFuturesClients
from ..core.transport.http import HttpRpcClient
from ..core.transport.ws.api import SocketRpcClient
from ..core.transport.ws.private_stream import PrivateStreamSocketClient
from ..core.transport.ws.streams import SocketStreamClient


@dataclass(kw_only=True, frozen=True)
class CoinMFuturesBase:
  """Base every generated COIN-M Futures leaf/router class subclasses -- holds the four
  already-built transport clients its `http`/`streams`/`private_streams`/`ws` children
  forward."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  private_streams_client: PrivateStreamSocketClient
  ws_client: SocketRpcClient

  @classmethod
  def new(cls, client: CoinMFuturesClients) -> Self:
    """Unpack COIN-M Futures' own real transport clients (design §5a's `client`-first
    forwarding convention) into this base's named fields."""
    return cls(
      http_client=client.http_client, streams_client=client.streams_client,
      private_streams_client=client.private_streams_client, ws_client=client.ws_client,
    )
