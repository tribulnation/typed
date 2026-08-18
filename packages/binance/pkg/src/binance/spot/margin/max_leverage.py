from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AdjustMaxLeverageResult(TypedDict):
  """Result of adjusting this account's cross margin max leverage."""

  success: bool
  """Whether the max leverage adjustment succeeded."""


class MaxLeverage(RpcEndpoint):
  """Adjust this account's cross margin max leverage."""

  async def max_leverage(
    self,
    *,
    max_leverage: int,
    validate: bool | None = None,
  ) -> AdjustMaxLeverageResult:
    """Adjust this account's cross margin max leverage.

    Args:
      max_leverage: Target max leverage. 5 or 3 for Cross Margin Classic; 10 for Cross Margin Pro (or 20 if compliance allows).

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#adjust-cross-margin-max-leverage)
    """
    params: dict = {
      'maxLeverage': max_leverage,
    }
    _Response = AdjustMaxLeverageResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/margin/max-leverage',
      params=params,
      validator=_validator,
      validate=validate,
    )
