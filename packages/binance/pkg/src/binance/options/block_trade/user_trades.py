from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class AccountBlockTradeLeg(TypedDict):
  """One executed leg of an account block trade."""

  id: NotRequired[str]
  """Unique ID of this leg."""
  createTime: NotRequired[Timestamp]
  """Time this leg's order was created."""
  updateTime: NotRequired[Timestamp]
  """Time this leg's order was last updated."""
  symbol: NotRequired[str]
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  orderId: NotRequired[str]
  """ID of this leg's order."""
  orderPrice: NotRequired[float]
  """Price of this leg's order."""
  orderQuantity: NotRequired[float]
  """Quantity of this leg's order."""
  orderStatus: NotRequired[
    Literal['ACCEPTED', 'PARTIALLY_FILLED', 'CANCELLED', 'FILLED', 'REJECTED']
  ]
  """Status of this leg's order."""
  executedQty: NotRequired[float]
  """Quantity executed so far for this leg's order."""
  executedAmount: NotRequired[float]
  """Amount executed so far for this leg's order."""
  fee: NotRequired[float]
  """Fee for this leg's trade."""
  orderType: NotRequired[Literal['LIMIT']]
  """Type of this leg's order."""
  orderSide: NotRequired[Literal['BUY', 'SELL']]
  """Buy/sell direction of this leg's order."""
  tradeId: NotRequired[int]
  """Trade ID for this leg's fill."""
  tradePrice: NotRequired[float]
  """Price this leg's fill traded at."""
  tradeQty: NotRequired[float]
  """Quantity this leg's fill traded."""
  tradeTime: NotRequired[Timestamp]
  """Time this leg's fill occurred."""
  liquidity: NotRequired[Literal['MAKER', 'TAKER']]
  """Whether this leg's fill was a taker or maker trade."""
  commission: NotRequired[float]
  """Commission charged for this leg's fill."""


class AccountBlockTrade(TypedDict):
  """One of the account's block trades."""

  parentOrderId: NotRequired[str]
  """ID of the parent block trade order these legs belong to."""
  crossType: NotRequired[str]
  """How this block trade was crossed."""
  blockTradeSettlementKey: NotRequired[str]
  """Key identifying this block trade for settlement/counterparty acceptance."""
  legs: NotRequired[list[AccountBlockTradeLeg]]
  """Executed legs of this block trade."""


class UserTrades(RpcEndpoint):
  """Get block trades for this account."""

  async def user_trades(
    self,
    *,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    underlying: str | None = None,
    validate: bool | None = None,
  ) -> list[AccountBlockTrade]:
    """Get block trades for this account.

    Args:
      start_time: Start time.
      end_time: End time.
      underlying: Underlying asset, e.g. BTCUSDT.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#account-block-trade-list)
    """
    params = {}
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if underlying is not None:
      params['underlying'] = underlying
    _Response = list[AccountBlockTrade]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/eapi/v1/block/user-trades',
      params=params,
      validator=_validator,
      validate=validate,
    )
