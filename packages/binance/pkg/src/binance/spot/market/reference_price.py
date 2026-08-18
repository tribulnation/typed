from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class ReferencePrice(TypedDict):
  """The reference price used for pegged-order support on a symbol."""

  symbol: str
  """Symbol."""
  referencePrice: str | None
  """Current reference price, or null when no reference price is currently set for the symbol."""
  timestamp: Timestamp
  """Timestamp when the reference price was valid."""


class ReferencePriceEndpoint(RpcEndpoint):
  """Query reference price"""

  async def reference_price(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> ReferencePrice:
    """Query the reference price used for pegged-order support on a symbol.

    Args:
      symbol: Symbol to query.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#query-reference-price)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = ReferencePrice
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/api/v3/referencePrice',
      params=params,
      validator=_validator,
      validate=validate,
    )
