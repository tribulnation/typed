from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProEarnAssetBalance(TypedDict):
  """Transferable earn asset balance."""

  asset: NotRequired[str]
  """Asset name."""
  amount: NotRequired[str]
  """Transferable amount."""


class EarnAssetBalance(RpcEndpoint):
  """Get Transferable Earn Asset Balance for Portfolio Margin"""

  async def earn_asset_balance(
    self,
    *,
    asset: str,
    transfer_type: Literal['EARN_TO_FUTURE', 'FUTURE_TO_EARN'],
    validate: bool | None = None,
  ) -> PmProEarnAssetBalance:
    """Get transferable earn asset balance for all types of Portfolio Margin account.

    Args:
      asset: `LDUSDT` only.
      transfer_type: Transfer direction.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-transferable-earn-asset-balance-for-portfolio-margin)
    """
    params: dict = {
      'asset': asset,
      'transferType': transfer_type,
    }
    _Response = PmProEarnAssetBalance
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/portfolio/earn-asset-balance',
      params=params,
      validator=_validator,
      validate=validate,
    )
