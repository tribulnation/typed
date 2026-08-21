"""The Hyperliquid client root."""

from dataclasses import dataclass, field
import asyncio as _asyncio
from eth_account.account import Account as _Account
from eth_account.signers.local import LocalAccount
from typed_core.exceptions import AuthError
from typed_core.http import HttpClient

from .core import ws_url as _resolve_ws_url
from .core.ws import SocketClient
from .info import Info
from .exchange.main import Exchange
from .streams import Streams

Wallet = LocalAccount | str | bytes | int


def _env_wallet(mainnet: bool = True) -> LocalAccount | None:
  """Load the network-specific wallet from the environment."""
  import os

  key = 'HYPERLIQUID_PRIVATE_KEY' if mainnet else 'HYPERLIQUID_TESTNET_PRIVATE_KEY'
  if (pk := os.getenv(key)) is not None:
    return _Account.from_key(pk)


def _parse_wallet(
  wallet: Wallet | None, *, mainnet: bool = True
) -> LocalAccount | None:
  """Parse an explicit wallet or load the network-specific environment wallet."""
  if wallet is None:
    return _env_wallet(mainnet=mainnet)
  if isinstance(wallet, LocalAccount):
    return wallet
  else:
    return _Account.from_key(wallet)


@dataclass(kw_only=True)
class Hyperliquid:
  """Composite Hyperliquid client for info, streams, and exchange APIs."""

  info: Info
  streams: Streams
  _exchange: Exchange | None = field(default=None, repr=False)

  @property
  def exchange(self) -> Exchange:
    """Authenticated Exchange API endpoints."""
    if self._exchange is None:
      raise AuthError(
        'Exchange is not available for public usage. Construct the client '
        'without `public=True` and provide a private key to use exchange '
        'methods.'
      )
    return self._exchange

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
  ):
    """Create a new Hyperliquid client, reachable over both HTTP and WebSocket.

    Args:
      wallet: Private key or account object. If omitted, falls back to the
        network-specific private key environment variable.
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      public: Allow usage without a wallet. If a wallet is provided or found
        in env, authenticated `exchange` methods are available.
      base_url: Custom HTTP API root. If provided, takes precedence over
        `mainnet`.
      ws_url: Custom WebSocket URL. If provided, takes precedence over
        `mainnet`.
    """
    http = HttpClient()
    ws = SocketClient(url=ws_url or _resolve_ws_url(mainnet))
    wallet = _parse_wallet(wallet, mainnet=mainnet)
    if wallet is None:
      if not public:
        raise ValueError(
          'Either provide a `wallet` argument or set `public=True` to use '
          'public endpoints.'
        )
      exchange = None
    else:
      exchange = Exchange.new(
        wallet,
        mainnet=mainnet,
        validate=validate,
        http=http,
        ws=ws,
        base_url=base_url,
        ws_url=ws_url,
      )
    return cls(
      info=Info.http(
        mainnet=mainnet,
        validate=validate,
        http=http,
        base_url=base_url,
      ),
      streams=Streams.of(ws, validate=validate),
      _exchange=exchange,
    )

  async def __aenter__(self):
    enters = [
      self.info.__aenter__(),
      self.streams.__aenter__(),
    ]
    if self._exchange is not None:
      enters.append(self._exchange.__aenter__())
    await _asyncio.gather(*enters)
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    exits = [
      self.info.__aexit__(exc_type, exc_value, traceback),
      self.streams.__aexit__(exc_type, exc_value, traceback),
    ]
    if self._exchange is not None:
      exits.append(self._exchange.__aexit__(exc_type, exc_value, traceback))
    await _asyncio.gather(*exits)
