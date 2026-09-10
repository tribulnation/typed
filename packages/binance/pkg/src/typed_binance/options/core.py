"""Options' own resolved core (`codegen/config.toml` `[python.cores.options]`, design §5c):
composes REST, market streams, and the private user-data stream, each holding its own
already-built transport client forwarded from `core.base.OptionsClients`.
"""

from typing_extensions import Self
from dataclasses import dataclass

from ..core.base import OptionsClients
from ..core.transport.http import HttpRpcClient
from ..core.transport.ws.private_stream import PrivateStreamSocketClient
from ..core.transport.ws.streams import SocketStreamClient


@dataclass(kw_only=True, frozen=True)
class OptionsBase:
  """Base every generated Options leaf/router class subclasses -- holds the three
  already-built transport clients its `http`/`streams`/`private_streams` children
  forward."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  private_streams_client: PrivateStreamSocketClient

  @classmethod
  def new(cls, client: OptionsClients) -> Self:
    """Unpack Options' own real transport clients (design §5a's `client`-first forwarding
    convention) into this base's named fields."""
    return cls(
      http_client=client.http_client, streams_client=client.streams_client,
      private_streams_client=client.private_streams_client,
    )
