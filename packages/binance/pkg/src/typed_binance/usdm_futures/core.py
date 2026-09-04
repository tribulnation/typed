"""USDⓈ-M Futures' own resolved core (`codegen/config.toml` `[python.cores.usdm_futures]`, design
§5c): composes REST, market streams, public streams, the private user-data stream, and
the WS API, each holding its own already-built transport client forwarded from
`core.base.UsdMFuturesClients`.
"""

from typing_extensions import Self
from dataclasses import dataclass

from ..core.base import UsdMFuturesClients
from ..core.transport.http import HttpRpcClient
from ..core.transport.ws.api import SocketRpcClient
from ..core.transport.ws.private_stream import PrivateStreamSocketClient
from ..core.transport.ws.streams import SocketStreamClient


@dataclass(kw_only=True, frozen=True)
class UsdMFuturesBase:
  """Base every generated USDⓈ-M Futures leaf/router class subclasses -- holds the five
  already-built transport clients its `http`/`streams`/`public_streams`/
  `private_streams`/`ws` children forward."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  public_streams_client: SocketStreamClient
  private_streams_client: PrivateStreamSocketClient
  ws_client: SocketRpcClient

  @classmethod
  def new(cls, client: UsdMFuturesClients) -> Self:
    """Unpack USDⓈ-M Futures' own real transport clients (design §5a's `client`-first
    forwarding convention) into this base's named fields."""
    return cls(
      http_client=client.http_client, streams_client=client.streams_client,
      public_streams_client=client.public_streams_client,
      private_streams_client=client.private_streams_client, ws_client=client.ws_client,
    )
