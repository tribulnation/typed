from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class GetIntradayMarginSettingResponse(TypedDict):
  """The account's intraday margin configuration."""

  setting: Literal[
    'INTRADAY_MARGIN_SETTING_UNSPECIFIED',
    'INTRADAY_MARGIN_SETTING_STANDARD',
    'INTRADAY_MARGIN_SETTING_INTRADAY',
  ]
  """The intraday margin configuration."""


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/cfm/intraday/margin_setting`."""

  async def get(self) -> GetIntradayMarginSettingResponse:
    """Get the account's current intraday margin setting for futures trading.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/futures/get-intraday-margin-setting)
    """
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/cfm/intraday/margin_setting',
      validator=validator(GetIntradayMarginSettingResponse),
    )
