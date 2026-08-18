from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProSwitchDeltaMode(TypedDict):
  """Switch delta mode result."""

  msg: NotRequired[str]
  """Result message."""


class SetDeltaMode(RpcEndpoint):
  """Switch Delta Mode"""

  async def set_delta_mode(
    self,
    *,
    delta_enabled: Literal['true', 'false'],
    validate: bool | None = None,
  ) -> PmProSwitchDeltaMode:
    """Switch the Delta mode for existing PM PRO / PM RETAIL accounts.

    Args:
      delta_enabled: `true` to enable Delta mode; `false` to disable Delta mode.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#switch-delta-mode)
    """
    params: dict = {
      'deltaEnabled': delta_enabled,
    }
    _Response = PmProSwitchDeltaMode
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/portfolio/delta-mode',
      params=params,
      validator=_validator,
      validate=validate,
    )
