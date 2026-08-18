from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OrderAmendment(TypedDict):
  """One amendment made to an order."""

  symbol: str
  """Symbol the amended order was placed on."""
  orderId: int
  """Order ID that was amended."""
  executionId: int
  """Execution ID assigned to this amendment."""
  origClientOrderId: str
  """Client order ID before this amendment."""
  newClientOrderId: str
  """Client order ID after this amendment."""
  origQty: str
  """Order quantity before this amendment, as a decimal string."""
  newQty: str
  """Order quantity after this amendment, as a decimal string."""
  time: int
  """Millisecond timestamp the amendment was made."""


class OrderAmendments(RpcEndpoint):
  """Query order amendments"""

  async def order_amendments(
    self,
    *,
    symbol: str,
    order_id: int,
    from_execution_id: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[OrderAmendment]:
    """Query all amendments of a single order.

    Args:
      symbol: Symbol to query.
      order_id: Order ID to query amendments for.
      from_execution_id: Execution ID to fetch from (inclusive).
      limit: Maximum number of amendments to return.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params: dict = {
      'symbol': symbol,
      'orderId': order_id,
    }
    if from_execution_id is not None:
      params['fromExecutionId'] = from_execution_id
    if limit is not None:
      params['limit'] = limit
    _Response = list[OrderAmendment]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/api/v3/order/amendments',
      params=params,
      validator=_validator,
      validate=validate,
    )
