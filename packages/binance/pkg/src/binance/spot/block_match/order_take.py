from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OrderTakeResult(TypedDict):
  """Result of accepting the order."""

  success: NotRequired[bool]
  """Whether the order was successfully accepted and the transaction completed."""


class OrderTake(RpcEndpoint):
  """Accept (take) an open Spot Block Matching order identified by its settlement key, completing the transaction."""

  async def order_take(
    self,
    *,
    settlement_key: str,
    validate: bool | None = None,
  ) -> OrderTakeResult:
    """Accept (take) an open Spot Block Matching order identified by its settlement key, completing the transaction.

    Args:
      settlement_key: Settlement key, from `spot.block_match.order_place`, identifying the order to accept.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-spot-block-matching/api/rest-api/~#order-take)
    """
    params: dict = {
      'settlementKey': settlement_key,
    }
    _Response = OrderTakeResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/block-match/order/take',
      params=params,
      validator=_validator,
      validate=validate,
    )
