"""`order.create` — Place an order over the WS Trade connection."""

from typing_extensions import Literal, NotRequired, TypedDict
from bybit.core.ws import TradeEndpoint


class OrderCreateArgs(TypedDict):
  """Order parameters, mirroring `POST /v5/order/create`."""

  category: Literal['spot', 'linear', 'inverse', 'option']
  """Product category."""
  symbol: str
  """Symbol name, for example `BTCUSDT`."""
  side: Literal['Buy', 'Sell']
  """Order side."""
  orderType: Literal['Market', 'Limit']
  """Order type."""
  qty: str
  """Order quantity."""
  price: NotRequired[str]
  """Limit price. Required for `orderType='Limit'`."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'PostOnly']]
  """Time in force."""


class OrderCreate(TradeEndpoint):
  """Build the `order.create` WS Trade command frame."""

  def order_create(self, args: OrderCreateArgs) -> dict:
    """Build the signed `order.create` frame this command would send, without sending it.

    Args:
      args: Command parameters, as the `order.create` command's `args[0]`.

    Raises:
      AuthError: The client holds no credentials.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/websocket/trade/guideline)
    """
    return self.socket.build_request('order.create', [args])
