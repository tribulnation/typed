from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesIncome(TypedDict):
  """A single account income (cash-flow) event."""

  symbol: NotRequired[str]
  """Trading symbol, if this income is symbol-associated."""
  incomeType: NotRequired[
    Literal[
      'TRANSFER',
      'WELCOME_BONUS',
      'REALIZED_PNL',
      'FUNDING_FEE',
      'COMMISSION',
      'INSURANCE_CLEAR',
      'REFERRAL_KICKBACK',
      'COMMISSION_REBATE',
      'API_REBATE',
      'CONTEST_REWARD',
      'CROSS_COLLATERAL_TRANSFER',
      'OPTIONS_PREMIUM_FEE',
      'OPTIONS_SETTLE_PROFIT',
      'INTERNAL_TRANSFER',
      'AUTO_EXCHANGE',
      'DELIVERED_SETTELMENT',
      'COIN_SWAP_DEPOSIT',
      'COIN_SWAP_WITHDRAW',
      'POSITION_LIMIT_INCREASE_FEE',
      'STRATEGY_UMFUTURES_TRANSFER',
      'FEE_RETURN',
      'BFUSD_REWARD',
    ]
  ]
  """Type of income event."""
  income: NotRequired[str]
  """Income amount, signed."""
  asset: NotRequired[str]
  """Asset this income is denominated in."""
  info: NotRequired[str]
  """Extra information about this income event."""
  time: NotRequired[int]
  """Millisecond epoch timestamp of this income event."""
  tranId: NotRequired[int]
  """Transaction identifier."""
  tradeId: NotRequired[str]
  """Trade identifier, if this income resulted from a trade."""


class Income(RpcEndpoint):
  """Query income history: realized PnL, funding fees, commissions, transfers, and other account cash-flow events. If `incomeType` is not sent, every income type is returned. If neither `startTime` nor `endTime` is sent, the most recent 7 days are returned. Income history only contains data for the last three months."""

  async def income(
    self,
    *,
    symbol: str | None = None,
    income_type: Literal[
      'TRANSFER',
      'WELCOME_BONUS',
      'REALIZED_PNL',
      'FUNDING_FEE',
      'COMMISSION',
      'INSURANCE_CLEAR',
      'REFERRAL_KICKBACK',
      'COMMISSION_REBATE',
      'API_REBATE',
      'CONTEST_REWARD',
      'CROSS_COLLATERAL_TRANSFER',
      'OPTIONS_PREMIUM_FEE',
      'OPTIONS_SETTLE_PROFIT',
      'INTERNAL_TRANSFER',
      'AUTO_EXCHANGE',
      'DELIVERED_SETTELMENT',
      'COIN_SWAP_DEPOSIT',
      'COIN_SWAP_WITHDRAW',
      'POSITION_LIMIT_INCREASE_FEE',
      'STRATEGY_UMFUTURES_TRANSFER',
      'FEE_RETURN',
      'BFUSD_REWARD',
    ]
    | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    page: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[UsdMFuturesIncome]:
    """Query income history: realized PnL, funding fees, commissions, transfers, and other account cash-flow events. If `incomeType` is not sent, every income type is returned. If neither `startTime` nor `endTime` is sent, the most recent 7 days are returned. Income history only contains data for the last three months.

    Args:
      symbol: Trading symbol to filter by.
      income_type: Income type to filter by. If omitted, every income type is returned.
      start_time: Timestamp in milliseconds, inclusive start.
      end_time: Timestamp in milliseconds, inclusive end.
      page: Pagination page number.
      limit: Maximum number of records to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-income-history)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if income_type is not None:
      params['incomeType'] = income_type
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    _Response = list[UsdMFuturesIncome]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/fapi/v1/income', params=params, validator=_validator, validate=validate
    )
