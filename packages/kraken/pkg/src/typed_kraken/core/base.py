"""Kraken client root and streams composition bases (design §5c): hand-written classes
holding each heterogeneous child's already-built transport, wrapped by the generated
`Kraken`/`Streams` composites.

`Kraken` composes three genuinely different children -- `spot` (HTTP), `streams` (two
WebSocket v2 connections), `trading_ws` (one of those same two connections, reached as
its own top-level surface rather than a `streams.*` subsection) -- so its own resolved
`core` (`KrakenBase`) is a *Base* holding one field per child, built once in `.new()`,
never a single shared transport every child forwards unchanged (design §5c, kraken's own
real, shipped shape being the section's own worked example).

`streams` itself further composes two children (`market_data`, `private`) that share one
of the two sockets `KrakenBase` already built and need the other one *additionally* --
`StreamsBase` is design §5a's own "extra caller-supplied value" forwarding mechanism,
layered on top of §5c's explicit `children` mapping (the two mechanisms "answer
independent questions" and compose without conflict, per design §5c's own text).
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .auth import TokenCache, resolve_credentials
from .transport.http import SPOT_API_URL, HttpRpcClient
from .transport.ws import SPOT_WS_AUTH_URL, SPOT_WS_URL, KrakenSocketClient


@dataclass(kw_only=True, frozen=True)
class StreamsBase:
  """The two physical WebSocket v2 connections `Streams` composes: public market data,
  and private (token-authenticated) channels -- the latter also shared with the
  top-level `TradingWs` surface (see `KrakenBase.new`, which builds both and passes the
  private one to each)."""

  private_client: KrakenSocketClient
  market_client: KrakenSocketClient

  @classmethod
  def new(cls, client: KrakenSocketClient, *, market_client: KrakenSocketClient) -> Self:
    """Build from the two already-connected sockets `KrakenBase.new` constructs.

    Args:
      client: The private (token-authenticated) socket -- forwarded as `private_client`.
      market_client: The public socket.
    """
    return cls(private_client=client, market_client=market_client)

  async def __aenter__(self) -> Self:
    await self.private_client.__aenter__()
    await self.market_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.private_client.__aexit__(exc_type, exc_value, traceback)
    await self.market_client.__aexit__(exc_type, exc_value, traceback)


@dataclass(kw_only=True)
class KrakenBase:
  """Kraken client root: builds and owns the three physical transports every generated
  composite (`Spot`, `Streams`, `TradingWs`) forwards unchanged -- one HTTP client, two
  WebSocket v2 sockets (public market data, private token-authenticated). `streams` and
  `trading_ws` share the same `private_client`: `streams.private`'s account-update
  channels and `trading_ws`'s order-entry methods both reach Kraken over the one
  authenticated connection.
  """

  spot_client: HttpRpcClient
  market_client: KrakenSocketClient
  private_client: KrakenSocketClient

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    private_key: str | None = None,
    public: bool = False,
    validate: bool = True,
  ) -> Self:
    """Build a Kraken Spot client.

    Args:
      api_key: Kraken API key; read from `KRAKEN_API_KEY` when omitted.
      private_key: Kraken private key; read from `KRAKEN_PRIVATE_KEY` when omitted.
      public: Build a credential-free client, usable only for public endpoints/channels.
      validate: Validate responses by default.
    """
    credentials = resolve_credentials(api_key, private_key, public=public)
    spot_client = HttpRpcClient(
      base_url=SPOT_API_URL, credentials=credentials, validate=validate
    )
    market_client = KrakenSocketClient.new(SPOT_WS_URL, validate=validate)
    private_client = KrakenSocketClient.new(
      SPOT_WS_AUTH_URL,
      token_cache=TokenCache() if credentials is not None else None,
      fetch_token=spot_client.get_ws_token if credentials is not None else None,
      validate=validate,
    )
    return cls(
      spot_client=spot_client, market_client=market_client, private_client=private_client,
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.spot_client.__aenter__(),
      self.market_client.__aenter__(),
      self.private_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.spot_client.__aexit__(exc_type, exc_value, traceback),
      self.market_client.__aexit__(exc_type, exc_value, traceback),
      self.private_client.__aexit__(exc_type, exc_value, traceback),
    )
