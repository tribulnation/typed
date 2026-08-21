"""Exchange endpoint base: RPC-shaped, wallet-signed, reachable over HTTP or the shared
WebSocket connection. See `spec/core.md` for the full surface writeup.
"""

from typing_extensions import Self
from dataclasses import dataclass
from datetime import timedelta

from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from typed_core.http import HttpClient

from typed_hyperliquid.core.endpoint.rpc import RpcClient, RpcEndpoint
from typed_hyperliquid.core.urls import http_base_url, ws_url as resolve_ws_url
from typed_hyperliquid.core.ws import SocketClient

from .auth import sign_l1_action, sign_user_signed_action
from .envelope import (
  ExchangeRequest,
  ExchangeResponse,
  OkResponse,
  ErrorResponse,
  raise_on_error,
)
from .transport.http import ExchangeHttpClient
from .transport.ws import ExchangeSocketClient

ExchangeClient = RpcClient
"""Transport for Hyperliquid exchange requests -- same shape as the shared `RpcClient`."""

Wallet = LocalAccount | str | bytes | int


def _parse_wallet(wallet: Wallet) -> LocalAccount:
  """Resolve a private key, byte string, or account object into a signer."""
  if isinstance(wallet, LocalAccount):
    return wallet
  return Account.from_key(wallet)


@dataclass(kw_only=True)
class ExchangeMixin(RpcEndpoint):
  """Base mixin for Hyperliquid exchange endpoint groups."""

  wallet: LocalAccount
  mainnet: bool

  @classmethod
  def http(
    cls,
    wallet: Wallet,
    *,
    mainnet: bool = True,
    validate: bool = True,
    http: HttpClient | None = None,
    base_url: str | None = None,
  ) -> Self:
    """Create an Exchange client with HTTP transport.

    Args:
      wallet: Private key or account object used to sign exchange actions.
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      http: Shared HTTP transport.
      base_url: Custom HTTP API root. If provided, takes
        precedence over `mainnet`.
    """
    client = ExchangeHttpClient(
      base_url=base_url or http_base_url(mainnet),
      validate=validate,
      http=http or HttpClient(),
    )
    return cls(
      client=client, wallet=_parse_wallet(wallet), mainnet=mainnet, validate=validate
    )

  @classmethod
  def ws_of(
    cls,
    wallet: Wallet,
    *,
    ws: SocketClient,
    mainnet: bool = True,
    validate: bool = True,
  ) -> Self:
    """Create an Exchange client from an existing WebSocket transport.

    Args:
      wallet: Private key or account object used to sign exchange actions.
      ws: Shared WebSocket transport.
      mainnet: Use mainnet signing rules when true,
        testnet signing rules when false.
      validate: Validate responses.
    """
    client = ExchangeSocketClient(ws=ws, validate=validate)
    return cls(
      client=client, wallet=_parse_wallet(wallet), mainnet=mainnet, validate=validate
    )

  @classmethod
  def ws(
    cls,
    wallet: Wallet,
    *,
    mainnet: bool = True,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ws_url: str | None = None,
  ) -> Self:
    """Create an Exchange client with WebSocket transport.

    Args:
      wallet: Private key or account object used to sign exchange actions.
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      timeout: WebSocket request timeout.
      ws_url: Custom WebSocket URL. If provided, takes
        precedence over `mainnet`.
    """
    ws = SocketClient(url=ws_url or resolve_ws_url(mainnet), timeout=timeout)
    return cls.ws_of(wallet, ws=ws, mainnet=mainnet, validate=validate)


__all__ = [
  'ExchangeClient',
  'ExchangeMixin',
  'ExchangeRequest',
  'ExchangeResponse',
  'OkResponse',
  'ErrorResponse',
  'raise_on_error',
  'ExchangeHttpClient',
  'ExchangeSocketClient',
  'sign_l1_action',
  'sign_user_signed_action',
  'Wallet',
]
