from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class SetIntradayMarginSettingRequest(TypedDict):
  """Request to change the intraday margin setting."""

  setting: Literal[
    'INTRADAY_MARGIN_SETTING_UNSPECIFIED',
    'INTRADAY_MARGIN_SETTING_STANDARD',
    'INTRADAY_MARGIN_SETTING_INTRADAY',
  ]
  """The margin setting for the account. Describes whether the account is opted in to receive increased leverage during weekdays (8am-4pm ET), excluding market holidays."""


class SetIntradayMarginSettingResponse(TypedDict):
  """Empty response confirming the setting was applied."""


@dataclass(frozen=True, kw_only=True)
class Set(RpcEndpoint):
  """`POST /api/v3/brokerage/cfm/intraday/margin_setting`."""

  async def set(
    self,
    set_intraday_margin_setting_request: SetIntradayMarginSettingRequest,
  ) -> SetIntradayMarginSettingResponse:
    """Set the account's intraday margin setting for futures trading — whether the account opts in to increased leverage during weekday market hours (8am-4pm ET, excluding market holidays).

    Args:
      set_intraday_margin_setting_request: The margin setting to apply.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/futures/set-intraday-margin-settings)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/brokerage/cfm/intraday/margin_setting',
      json=set_intraday_margin_setting_request,
      validator=validator(SetIntradayMarginSettingResponse),
    )
