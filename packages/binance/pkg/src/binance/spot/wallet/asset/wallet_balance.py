from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class WalletBalance(TypedDict):
  """Total balance of a single wallet."""

  activate: bool
  """Whether this wallet is activated for the account."""
  balance: str
  """Total balance of this wallet, denominated in `quoteAsset` (BTC by default)."""
  walletName: str
  """Wallet name, e.g. "Spot"."""


class WalletBalanceEndpoint(RpcEndpoint):
  """Query the total balance of each of the account's wallets (Spot, Margin, Funding, Futures, ...), valued in BTC."""

  async def __call__(
    self,
    *,
    quote_asset: str | None = None,
    validate: bool | None = None,
  ) -> list[WalletBalance]:
    """Query the total balance of each of the account's wallets (Spot, Margin, Funding, Futures, ...), valued in BTC.

    Args:
      quote_asset: Asset each wallet's balance is denominated in.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#query-user-wallet-balance)
    """
    params = {}
    if quote_asset is not None:
      params['quoteAsset'] = quote_asset
    _Response = list[WalletBalance]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/asset/wallet/balance',
      params=params,
      validator=_validator,
      validate=validate,
    )
