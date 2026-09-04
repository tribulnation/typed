"""Hyperliquid client root: lifecycle and shared transport wiring.

Every resolved `core` this client declares (`codegen/config.toml`'s `[python.cores]`, design §5c)
-- `info`, `exchange`, `streams` -- is a genuinely different kind of surface (a plain RPC
mixin, a wallet-signing RPC mixin, a subscribe-only mixin), so unlike a single-transport
client (alchemy's `AlchemyTransport`), there is no one shared low-level object every core
forwards unchanged. `ClientBase` builds one `HttpClient` and one `SocketClient`, shares both
across every surface that needs them, and owns lifecycle (`.new()`,
`__aenter__`/`__aexit__`); the generated root class (`typed_hyperliquid.main.Hyperliquid`)
subclasses `ClientBase` alone, never also a resolved core (design §4) -- `Hyperliquid`
itself declares no direct endpoints.
"""

from typing_extensions import Self
from dataclasses import dataclass
from eth_account.account import Account as _Account
from eth_account.signers.local import LocalAccount

from typed_core.http import HttpClient

from .urls import http_base_url, ws_url as resolve_ws_url
from .ws import SocketClient
from ..info.core.transport.http import InfoHttpClient
from ..info.core.transport.ws import InfoSocketClient
from ..exchange.core.transport.http import ExchangeHttpClient
from ..exchange.core.transport.ws import ExchangeSocketClient

Wallet = LocalAccount | str | bytes | int


def _env_wallet(mainnet: bool = True) -> LocalAccount | None:
  """Load the network-specific wallet from the environment."""
  import os

  key = 'HYPERLIQUID_PRIVATE_KEY' if mainnet else 'HYPERLIQUID_TESTNET_PRIVATE_KEY'
  if (pk := os.getenv(key)) is not None:
    return _Account.from_key(pk)


def _parse_wallet(wallet: Wallet | None, *, mainnet: bool = True) -> LocalAccount | None:
  """Parse an explicit wallet or load the network-specific environment wallet."""
  if wallet is None:
    return _env_wallet(mainnet=mainnet)
  if isinstance(wallet, LocalAccount):
    return wallet
  return _Account.from_key(wallet)


@dataclass(kw_only=True, frozen=True)
class ClientBase:
  """Root lifecycle: constructs and owns the shared HTTP/WebSocket transports every
  resolved `core` forwards. The generated root class (`main.Hyperliquid`) subclasses this
  and this alone (design §4) -- never also a resolved `core`.
  """

  info_client: InfoHttpClient
  info_ws_client: InfoSocketClient
  exchange_client: ExchangeHttpClient
  exchange_ws_client: ExchangeSocketClient
  streams_client: SocketClient
  wallet: LocalAccount | None
  mainnet: bool
  validate: bool
  http: HttpClient
  """The shared low-level HTTP transport `info_client`/`exchange_client` both wrap --
  entered/exited exactly once here, rather than once per wrapping surface."""

  @classmethod
  def new(
    cls,
    wallet: Wallet | None = None,
    /,
    *,
    mainnet: bool = True,
    validate: bool = True,
    public: bool = False,
    base_url: str | None = None,
    ws_url: str | None = None,
  ) -> Self:
    """Create a new Hyperliquid client, reachable over both HTTP and WebSocket.

    Args:
      wallet: Private key or account object. If omitted, falls back to the
        network-specific private key environment variable.
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      public: Allow usage without a wallet. If a wallet is provided or found in env,
        authenticated `exchange` methods are available; without one, `exchange` still
        constructs, but every call raises `AuthError` until a wallet is provided.
      base_url: Custom HTTP API root. If provided, takes precedence over `mainnet`.
      ws_url: Custom WebSocket URL. If provided, takes precedence over `mainnet`.
    """
    parsed_wallet = _parse_wallet(wallet, mainnet=mainnet)
    if parsed_wallet is None and not public:
      raise ValueError(
        'Either provide a `wallet` argument or set `public=True` to use public endpoints.'
      )
    http = HttpClient()
    ws = SocketClient(url=ws_url or resolve_ws_url(mainnet))
    resolved_base_url = base_url or http_base_url(mainnet)
    return cls(
      info_client=InfoHttpClient(base_url=resolved_base_url, http=http),
      info_ws_client=InfoSocketClient(ws=ws),
      exchange_client=ExchangeHttpClient(base_url=resolved_base_url, http=http),
      exchange_ws_client=ExchangeSocketClient(ws=ws),
      streams_client=ws,
      wallet=parsed_wallet,
      mainnet=mainnet,
      validate=validate,
      http=http,
    )

  async def __aenter__(self) -> Self:
    await self.http.__aenter__()
    await self.streams_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)
    await self.streams_client.__aexit__(exc_type, exc_value, traceback)
