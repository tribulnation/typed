from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FundingAsset(TypedDict):
  """Funding wallet balance of a single asset."""

  asset: str
  """Asset symbol."""
  free: str
  """Available (unlocked) balance."""
  locked: str
  """Locked balance."""
  freeze: str
  """Frozen balance."""
  withdrawing: str
  """Balance currently being withdrawn."""
  btcValuation: str
  """Total balance, denominated in BTC. `"0"` unless `needBtcValuation` is `true`."""


class FundingWallet(RpcEndpoint):
  """Query the Funding wallet's balances. Currently supports the following business assets: Binance Pay, Binance Card, Binance Gift Card, Stock Token."""

  async def __call__(
    self,
    *,
    asset: str | None = None,
    need_btc_valuation: Literal['true', 'false'] | None = None,
    validate: bool | None = None,
  ) -> list[FundingAsset]:
    """Query the Funding wallet's balances. Currently supports the following business assets: Binance Pay, Binance Card, Binance Gift Card, Stock Token.

    Args:
      asset: Asset to query. Returns every asset when omitted.
      need_btc_valuation: Whether to include each asset's BTC valuation.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#funding-wallet)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if need_btc_valuation is not None:
      params['needBtcValuation'] = need_btc_valuation
    _Response = list[FundingAsset]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/asset/get-funding-asset',
      params=params,
      validator=_validator,
      validate=validate,
    )
