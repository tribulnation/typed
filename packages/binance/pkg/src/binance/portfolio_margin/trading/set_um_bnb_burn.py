from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmToggleBnbBurnOnUmFuturesTrade(TypedDict):
  """Change user's BNB Fee Discount for UM Futures (Fee Discount On or Fee Discount Off ) on ***EVERY symbol***."""

  code: NotRequired[int]
  """Code."""
  msg: NotRequired[str]
  """Msg."""


class SetUmBnbBurn(RpcEndpoint):
  """Toggle BNB Burn On UM Futures Trade"""

  async def set_um_bnb_burn(
    self,
    *,
    fee_burn: Literal['true', 'false'],
    validate: bool | None = None,
  ) -> PmToggleBnbBurnOnUmFuturesTrade:
    """Change user's BNB Fee Discount for UM Futures (Fee Discount On or Fee Discount Off ) on ***EVERY symbol***.

    Args:
      fee_burn: \"true": Fee Discount On; "false": Fee Discount Off.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#toggle-bnb-burn-on-um-futures-trade)
    """
    params: dict = {
      'feeBurn': fee_burn,
    }
    _Response = PmToggleBnbBurnOnUmFuturesTrade
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/papi/v1/um/feeBurn',
      params=params,
      validator=_validator,
      validate=validate,
    )
