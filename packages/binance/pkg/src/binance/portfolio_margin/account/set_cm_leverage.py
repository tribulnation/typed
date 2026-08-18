from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmChangeCmInitialLeverage(TypedDict):
  """Change user's initial leverage of specific symbol in CM."""

  leverage: NotRequired[int]
  """current initial leverage."""
  maxQty: NotRequired[str]
  """maximum quantity of base asset."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""


class SetCmLeverage(RpcEndpoint):
  """Change CM Initial Leverage"""

  async def set_cm_leverage(
    self,
    *,
    symbol: str,
    leverage: int,
    validate: bool | None = None,
  ) -> PmChangeCmInitialLeverage:
    """Change user's initial leverage of specific symbol in CM.

    Args:
      symbol: Trading pair symbol.
      leverage: target initial leverage.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#change-cm-initial-leverage)
    """
    params: dict = {
      'symbol': symbol,
      'leverage': leverage,
    }
    _Response = PmChangeCmInitialLeverage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/papi/v1/cm/leverage',
      params=params,
      validator=_validator,
      validate=validate,
    )
