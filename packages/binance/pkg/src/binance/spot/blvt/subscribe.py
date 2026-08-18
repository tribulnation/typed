from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BlvtSubscription(TypedDict):
  """Result of subscribing to (buying) a leveraged token."""

  id: int
  """Subscription record identifier."""
  status: Literal['S', 'P', 'F']
  """Subscription status."""
  tokenName: str
  """Leveraged token name subscribed to."""
  amount: str
  """Token amount subscribed."""
  cost: str
  """Subscription cost, in USDT."""
  timestamp: Timestamp
  """Time the subscription was processed."""


class Subscribe(RpcEndpoint):
  """Subscribe BLVT (USER_DATA)"""

  async def subscribe(
    self,
    *,
    token_name: str,
    cost: float,
    validate: bool | None = None,
  ) -> BlvtSubscription:
    """Subscribe to (buy) a Binance Leveraged Token, spending spot balance.

    Args:
      token_name: Leveraged token name, e.g. `BTCDOWN`, `BTCUP`.
      cost: Spot balance to spend subscribing.

    References:
      - [Official docs](https://github.com/binance/binance-api-swagger)
    """
    params: dict = {
      'tokenName': token_name,
      'cost': cost,
    }
    _Response = BlvtSubscription
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/blvt/subscribe',
      params=params,
      validator=_validator,
      validate=validate,
    )
