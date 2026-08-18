from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class ArithmeticMeanReferencePriceCalculation(TypedDict):
  """Reference price calculated by the matching engine as an arithmetic mean."""

  symbol: str
  """Symbol."""
  calculationType: Literal['ARITHMETIC_MEAN']
  """Calculation method."""
  bucketCount: int
  """Number of time buckets averaged over."""
  bucketWidthMs: int
  """Width of each time bucket, in milliseconds."""


class ExternalReferencePriceCalculation(TypedDict):
  """Reference price calculated outside the matching engine."""

  symbol: str
  """Symbol."""
  calculationType: Literal['EXTERNAL']
  """Calculation method."""
  externalCalculationId: int
  """Identifier of the external calculation source."""


class ReferencePriceCalculation(WsRpcEndpoint):
  """Query reference price calculation"""

  async def reference_price_calculation(
    self,
    *,
    symbol: str,
    symbol_status: Literal['TRADING', 'HALT', 'BREAK'] | None = None,
    validate: bool | None = None,
  ) -> ArithmeticMeanReferencePriceCalculation | ExternalReferencePriceCalculation:
    """Describes how the reference price is calculated for a given symbol.

    Args:
      symbol: Symbol to query.
      symbol_status: Filter for symbols with this trading status.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#query-reference-price-calculation)
    """
    params: dict = {
      'symbol': symbol,
    }
    if symbol_status is not None:
      params['symbolStatus'] = symbol_status
    _Response = (
      ArithmeticMeanReferencePriceCalculation | ExternalReferencePriceCalculation
    )
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.request(
      'referencePrice.calculation',
      params=params,
      validator=_validator,
      validate=validate,
    )
