"""`private/get_settlement_history_by_currency` — `private/get_settlement_history_by_currency`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Settlement(TypedDict):
  funding: NotRequired[float]
  """funding (in base currency ; settlement for perpetual product only)"""
  funded: NotRequired[float]
  """funded amount (bankruptcy only)"""
  index_price: float
  """underlying index price at time of event (in quote currency; settlement and delivery only)"""
  instrument_name: str
  """instrument name (settlement and delivery only)"""
  mark_price: NotRequired[float]
  """mark price for at the settlement time (in quote currency; settlement and delivery only)"""
  position: float
  """position size (in quote currency; settlement and delivery only)"""
  profit_loss: NotRequired[float]
  """Platform-wide aggregate realized profit and loss for this settlement event, in base currency. This is the sum of the realized P&L of every position holder at the settlement or delivery price — it is **not** a per-account value. Present for `settlement` and `delivery` types only."""
  session_bankruptcy: NotRequired[float]
  """value of session bankruptcy (in base currency; bankruptcy only)"""
  session_profit_loss: float
  """Platform-wide aggregate total session profit and loss for this settlement event, in base currency. This is the sum of each position holder's session P&L (combining realized and unrealized components) across all users who held positions in the instrument — it is **not** a per-account value."""
  session_tax: NotRequired[float]
  """total amount of paid taxes/fees (in base currency; bankruptcy only)"""
  session_tax_rate: NotRequired[float]
  """rate of paid taxes/fees (in base currency; bankruptcy only)"""
  socialized: NotRequired[float]
  """the amount of the socialized losses (in base currency; bankruptcy only)"""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch)"""
  type: Literal['settlement', 'delivery', 'bankruptcy']
  """The type of settlement. `settlement`, `delivery` or `bankruptcy`."""


class GetSettlementHistoryByCurrencyResult(TypedDict):
  continuation: str
  """Continuation token for pagination."""
  settlements: list[Settlement]
  """Settlement, delivery, or bankruptcy events matching the query."""


validate_get_settlement_history_by_currency = validator[
  GetSettlementHistoryByCurrencyResult
](GetSettlementHistoryByCurrencyResult)


class GetSettlementHistoryByCurrency(RpcEndpoint):
  """`private/get_settlement_history_by_currency`."""

  async def get_settlement_history_by_currency(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    type: Literal['settlement', 'delivery', 'bankruptcy'] | None = None,
    count: int | None = None,
    continuation: str | None = None,
    search_start_timestamp: int | None = None,
    validate: bool | None = None,
  ) -> GetSettlementHistoryByCurrencyResult:
    """Retrieves settlement, delivery, and bankruptcy events that have affected your account for a specific currency. Settlements occur when futures or options contracts expire and are settled at the delivery price.

    Results can be filtered by settlement type and timestamp. Use pagination parameters (`count` and `continuation`) to retrieve large settlement histories. This data is useful for tracking account-affecting settlement events and understanding how contract expirations impact your account.

    Args:
      currency: The currency symbol
      type: Settlement type
      count: Number of requested items, default - `20`, maximum - `1000`
      continuation: Continuation token for pagination
      search_start_timestamp: The latest timestamp to return result from (milliseconds since the UNIX epoch)
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/trading/private-get_settlement_history_by_currency)
    """
    params: dict = {
      'currency': currency,
    }
    if type is not None:
      params['type'] = type
    if count is not None:
      params['count'] = count
    if continuation is not None:
      params['continuation'] = continuation
    if search_start_timestamp is not None:
      params['search_start_timestamp'] = search_start_timestamp
    return await self.authed_request(
      'private/get_settlement_history_by_currency',
      params=params,
      validator=validate_get_settlement_history_by_currency,
      validate=validate,
    )
