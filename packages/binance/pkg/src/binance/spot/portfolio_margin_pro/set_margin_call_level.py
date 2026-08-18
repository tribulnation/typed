from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProSetMarginCallLevel(TypedDict):
  """Set margin call level result."""

  marginCallLevel: NotRequired[str]
  """The margin call level that was set."""


class SetMarginCallLevel(RpcEndpoint):
  """Set Margin Call Level"""

  async def set_margin_call_level(
    self,
    *,
    margin_call_level: float,
    validate: bool | None = None,
  ) -> PmProSetMarginCallLevel:
    """Set the margin call level for a Portfolio Margin account. When the account's uniMMR drops to the specified level, a notification will be sent via email and SMS.

    Args:
      margin_call_level: The value must be within the range [1.1, 2.0].

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#set-margin-call-level)
    """
    params: dict = {
      'marginCallLevel': margin_call_level,
    }
    _Response = PmProSetMarginCallLevel
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/portfolio/margin-call-level',
      params=params,
      validator=_validator,
      validate=validate,
    )
