from json import dumps
from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DustTransferDetail(TypedDict):
  """Conversion result for a single source asset."""

  amount: str
  """Amount of the source asset converted."""
  fromAsset: str
  """Source asset converted."""
  operateTime: int
  """Conversion time, as milliseconds since epoch."""
  serviceChargeAmount: str
  """BNB service charge for this asset."""
  tranId: int
  """Transaction ID."""
  transferedAmount: str
  """BNB amount credited for this asset."""


class DustTransferResult(TypedDict):
  """Result of converting one or more dust assets to BNB."""

  totalServiceCharge: str
  """Total BNB service charge across all converted assets."""
  totalTransfered: str
  """Total BNB amount credited."""
  transferResult: list[DustTransferDetail]
  """One entry per asset converted."""


class Transfer(RpcEndpoint):
  """Convert dust asset balances directly to BNB. Legacy predecessor to `spot.wallet.asset.dust_convert.convert`, which also supports a non-BNB target asset; still documented and live. The API key must have `Enable Spot & Margin Trading` permission."""

  async def transfer(
    self,
    *,
    asset: list[str],
    account_type: Literal['SPOT', 'MARGIN'] | None = None,
    validate: bool | None = None,
  ) -> DustTransferResult:
    """Convert dust asset balances directly to BNB. Legacy predecessor to `spot.wallet.asset.dust_convert.convert`, which also supports a non-BNB target asset; still documented and live. The API key must have `Enable Spot & Margin Trading` permission.

    Args:
      asset: Asset(s) to convert, sent as repeated `asset` query params, e.g. `asset=BTC&asset=USDT`.
      account_type: Wallet the assets are converted from.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-transfer)
    """
    params: dict = {
      'asset': dumps(asset, separators=(',', ':')),
    }
    if account_type is not None:
      params['accountType'] = account_type
    _Response = DustTransferResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/asset/dust',
      params=params,
      validator=_validator,
      validate=validate,
    )
