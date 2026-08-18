from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DustBtcAsset(TypedDict):
  """A single asset available for dust-to-BNB conversion."""

  asset: str
  """Source asset symbol."""
  assetFullName: str
  """Source asset full name."""
  amountFree: str
  """Convertible (available) balance of the source asset."""
  toBTC: str
  """Amount this source asset would yield, denominated in BTC."""
  toBNB: str
  """Amount this source asset would yield in BNB, before commission."""
  toBNBOffExchange: str
  """Amount this source asset would yield in BNB, after commission."""
  exchange: str
  """Commission fee charged on this asset's conversion."""


class DustBtcAssets(TypedDict):
  """Preview of a dust-to-BNB conversion."""

  details: list[DustBtcAsset]
  """One entry per convertible source asset."""
  totalTransferBtc: str
  """Total convertible amount, denominated in BTC."""
  totalTransferBNB: str
  """Total convertible amount, denominated in BNB."""
  dribbletPercentage: str
  """Commission rate charged on the conversion."""


class DustBtc(RpcEndpoint):
  """Preview which asset balances are eligible for dust-to-BNB conversion via `spot.wallet.asset.dust.transfer`, and the amount each would yield."""

  async def __call__(
    self,
    *,
    account_type: Literal['SPOT', 'MARGIN'] | None = None,
    validate: bool | None = None,
  ) -> DustBtcAssets:
    """Preview which asset balances are eligible for dust-to-BNB conversion via `spot.wallet.asset.dust.transfer`, and the amount each would yield.

    Args:
      account_type: Wallet the assets would be converted from.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-assets-that-can-be-converted-into-bnb)
    """
    params = {}
    if account_type is not None:
      params['accountType'] = account_type
    _Response = DustBtcAssets
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/asset/dust-btc',
      params=params,
      validator=_validator,
      validate=validate,
    )
