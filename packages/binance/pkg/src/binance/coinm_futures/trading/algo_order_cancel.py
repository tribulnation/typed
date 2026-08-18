from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMCancelAlgoOrderResult(TypedDict):
  """Cancellation acknowledgement for the algo order."""

  algoId: int
  """Algo order ID."""
  clientAlgoId: NotRequired[str]
  """Client algo order ID."""
  code: NotRequired[str]
  """Result code for the cancellation. Typed as a string, not an integer, matching the sibling USD-M `algoOrder` endpoint's SDK model (`CancelAlgoOrderResponse.code`) — unusual for a Binance result code, but that is what the confirmed sibling shape uses."""
  msg: NotRequired[str]
  """Result message for the cancellation."""


class AlgoOrderCancel(RpcEndpoint):
  """Cancel Algo Order"""

  async def algo_order_cancel(
    self,
    *,
    algo_id: int | None = None,
    client_algo_id: str | None = None,
    validate: bool | None = None,
  ) -> CoinMCancelAlgoOrderResult:
    """Cancel an active algo (conditional) order. See `algo_order_place`'s `notes` for this group's source-confidence caveat.

    Args:
      algo_id: Algo order ID. Either `algoId` or `clientAlgoId` must be sent.
      client_algo_id: Client algo order ID. Either `algoId` or `clientAlgoId` must be sent.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#cancel-algo-order)
    """
    params = {}
    if algo_id is not None:
      params['algoId'] = algo_id
    if client_algo_id is not None:
      params['clientAlgoId'] = client_algo_id
    _Response = CoinMCancelAlgoOrderResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/dapi/v1/algoOrder',
      params=params,
      validator=_validator,
      validate=validate,
    )
