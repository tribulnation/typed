from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProDeleteMarginCallLevel(TypedDict):
  """Delete margin call level result."""

  msg: NotRequired[str]
  """Result message."""


class DeleteMarginCallLevel(RpcEndpoint):
  """Delete Margin Call Level"""

  async def delete_margin_call_level(
    self,
    *,
    validate: bool | None = None,
  ) -> PmProDeleteMarginCallLevel:
    """Delete the margin call level for a Portfolio Margin account.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#delete-margin-call-level)
    """
    _Response = PmProDeleteMarginCallLevel
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/sapi/v1/portfolio/margin-call-level',
      validator=_validator,
      validate=validate,
    )
