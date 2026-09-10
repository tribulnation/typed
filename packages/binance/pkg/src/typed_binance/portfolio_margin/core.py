"""Portfolio Margin's own resolved core (`codegen/config.toml` `[python.cores.portfolio_margin]`,
design §5c): composes REST and the private user-data stream, each holding its own
already-built transport client forwarded from `core.base.PortfolioMarginClients`.
"""

from typing_extensions import Self
from dataclasses import dataclass

from ..core.base import PortfolioMarginClients
from ..core.transport.http import HttpRpcClient
from ..core.transport.ws.private_stream import PrivateStreamSocketClient


@dataclass(kw_only=True, frozen=True)
class PortfolioMarginBase:
  """Base every generated Portfolio Margin leaf/router class subclasses -- holds the two
  already-built transport clients its `http`/`private_streams` children forward."""

  http_client: HttpRpcClient
  private_streams_client: PrivateStreamSocketClient

  @classmethod
  def new(cls, client: PortfolioMarginClients) -> Self:
    """Unpack Portfolio Margin's own real transport clients (design §5a's `client`-first
    forwarding convention) into this base's named fields."""
    return cls(
      http_client=client.http_client, private_streams_client=client.private_streams_client,
    )
