"""KuCoin WebSocket connections: a Spot/Margin instance and a Futures instance.

Both share `SocketStreamClient` (`kucoin.core.transport.ws`) but are genuinely separate
connections, each with its own bullet-token endpoint — see `spec/core.md` §Transport.
`Streams` composes them plainly, the way `bybit.Ws` composes sockets that each need their
own resolved URL, rather than reflectively: there is no shared base URL between them.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from kucoin.core import (
  Credentials,
  DEFAULT_API_URL,
  FUTURES_API_URL,
  HttpRpcClient,
  SocketStreamClient,
  StreamEndpoint,
)
from .market import Market
from .private import Private


class SpotMarginChannels(Market, Private):
  """Public and private channels on the Spot/Margin instance — one physical connection
  serves both, see `SocketStreamClient`."""


@dataclass(kw_only=True)
class Streams:
  """Every KuCoin WebSocket connection, reachable from the one client root.

  `futures` is a bare `StreamEndpoint` — its connection is already lazily openable, but
  no channel is wired onto it yet. Ticker, OrderBook, Klines and the rest of the Futures
  private surfaces await `client-spec`; see `spec/core.md`.
  """

  spot_margin: SpotMarginChannels
  futures: StreamEndpoint

  @classmethod
  def new(
    cls, *, credentials: Credentials | None = None, validate: bool = True
  ) -> Self:
    """Build both connections against an already-resolved `Credentials`.

    Both open with a **private** bullet token whenever `credentials` is set — one
    connection then serves both public and private topics (`SocketStreamClient`'s own
    docstring) — and a public one otherwise, restricting each connection to public
    topics only. An `authed_subscribe` call on a credential-free connection still fails
    fast with `AuthError`, before any network I/O, rather than round-tripping to KuCoin
    for a rejection (see `streams.private.balance.Balance.balance`).

    Args:
      credentials: Shared by both instances.
      validate: Validate pushed payloads by default.
    """
    private = credentials is not None
    return cls(
      spot_margin=SpotMarginChannels(
        client=SocketStreamClient.new(
          bullet=HttpRpcClient(base_url=DEFAULT_API_URL, credentials=credentials),
          private=private,
          validate=validate,
        )
      ),
      futures=StreamEndpoint(
        client=SocketStreamClient.new(
          bullet=HttpRpcClient(base_url=FUTURES_API_URL, credentials=credentials),
          private=private,
          validate=validate,
        )
      ),
    )

  def _clients(self):
    return (self.spot_margin.client, self.futures.client)

  async def __aenter__(self):
    await asyncio.gather(*(client.__aenter__() for client in self._clients()))
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      *(client.__aexit__(exc_type, exc_value, traceback) for client in self._clients())
    )
