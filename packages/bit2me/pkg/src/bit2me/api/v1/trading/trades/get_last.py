from decimal import Decimal
from bit2me.types import OrderSide
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(list[list[OrderSide | Decimal]])


class GetLast(RpcEndpoint):
  async def get_last(
    self,
    *,
    symbol: str,
    limit: float | None = None,
    validate: bool | None = None,
  ) -> list[list[OrderSide | Decimal]]:
    """Get a list of last trades. Returns the last 50 trades by default.

    Args:
      symbol: Market symbol to fetch the latest trades for.
      limit: The number of trades to retrieve
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/marketdata/GET/v1/trading/trade/last)
    """
    params: dict = {
      'symbol': symbol,
    }
    if limit is not None:
      params['limit'] = limit
    return await self.request(
      'GET',
      '/v1/trading/trade/last',
      params=params,
      validator=validate_response,
      validate=validate,
    )
