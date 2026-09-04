"""Spot's own resolved core (`codegen/config.toml` `[python.cores.spot]`, design §5c): composes
REST, market-data streams, and the WS API, each holding its own already-built transport
client forwarded from `core.base.SpotClients`.
"""

from typing_extensions import Self
from dataclasses import dataclass

from ..core.base import SpotClients
from ..core.transport.http import HttpRpcClient
from ..core.transport.ws.api import SocketRpcClient
from ..core.transport.ws.streams import SocketStreamClient


@dataclass(kw_only=True, frozen=True)
class SpotBase:
  """Base every generated Spot leaf/router class subclasses -- holds the three already-
  built transport clients `spot`'s own `http`/`streams`/`ws` children forward."""

  http_client: HttpRpcClient
  streams_client: SocketStreamClient
  ws_client: SocketRpcClient

  @classmethod
  def new(cls, client: SpotClients) -> Self:
    """Unpack Spot's own real transport clients (design §5a's `client`-first forwarding
    convention) into this base's named fields."""
    return cls(
      http_client=client.http_client, streams_client=client.streams_client, ws_client=client.ws_client,
    )
