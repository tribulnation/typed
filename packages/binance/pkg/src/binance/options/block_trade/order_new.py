from json import dumps
from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class NewBlockTradeOrderLeg(TypedDict):
  """One leg of a new block trade order."""

  symbol: str
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  side: Literal['BUY', 'SELL']
  """Buy/sell direction."""
  type: Literal['LIMIT']
  """Order type. Only LIMIT is documented for Options."""
  quantity: str
  """Order quantity."""
  price: NotRequired[str]
  """Order price."""


class NewBlockTradeOrderResultLeg(TypedDict):
  """One leg of the block trade order as accepted by the venue."""

  symbol: NotRequired[str]
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Buy/sell direction."""
  quantity: NotRequired[str]
  """Order quantity."""
  price: NotRequired[str]
  """Order price."""


class NewBlockTradeOrderResult(TypedDict):
  """The block trade order as accepted by the venue."""

  blockTradeSettlementKey: NotRequired[str]
  """Key identifying this block trade for settlement/counterparty acceptance."""
  expireTime: NotRequired[Timestamp]
  """Time the block trade order expires if not accepted."""
  liquidity: NotRequired[Literal['MAKER', 'TAKER']]
  """Whether this side of the block trade is the maker or the taker."""
  status: NotRequired[str]
  """Block trade order status."""
  legs: NotRequired[list[NewBlockTradeOrderResultLeg]]
  """Legs of the block trade order."""


class OrderNew(RpcEndpoint):
  """Send in a new block trade order. A market-maker-only endpoint, distinct from the regular order book: a block trade is negotiated off-book between two counterparties and settled once the other side accepts it (see `options.block_trade.order_accept`)."""

  async def order_new(
    self,
    *,
    liquidity: Literal['MAKER', 'TAKER'],
    legs: list[NewBlockTradeOrderLeg],
    validate: bool | None = None,
  ) -> NewBlockTradeOrderResult:
    """Send in a new block trade order. A market-maker-only endpoint, distinct from the regular order book: a block trade is negotiated off-book between two counterparties and settled once the other side accepts it (see `options.block_trade.order_accept`).

    Args:
      liquidity: Whether this side of the block trade is the maker or the taker.
      legs: Legs of the block trade order. Only a single leg is currently supported.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#new-block-trade-order)
    """
    params: dict = {
      'liquidity': liquidity,
      'legs': dumps(legs, separators=(',', ':')),
    }
    _Response = NewBlockTradeOrderResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/eapi/v1/block/order/create',
      params=params,
      validator=_validator,
      validate=validate,
    )
