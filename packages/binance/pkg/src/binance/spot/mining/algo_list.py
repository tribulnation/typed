from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MiningAlgo(TypedDict):
  """One mining pool algorithm."""

  algoName: NotRequired[str]
  """Algorithm name, e.g. SHA256-BTC."""
  algoId: NotRequired[int]
  """Algorithm identifier."""
  poolIndex: NotRequired[int]
  """Pool index."""
  unit: NotRequired[str]
  """Hashrate unit, e.g. h/s."""


class MiningAlgoListResponse(TypedDict):
  """Mining algo list response frame. This product line wraps its business data in {code,msg,data} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[int]
  """Response code. 0 indicates success."""
  msg: NotRequired[str]
  """Response message."""
  data: NotRequired[list[MiningAlgo]]
  """Mining algorithms."""


class AlgoList(RpcEndpoint):
  """Query mining pool algorithms."""

  async def algo_list(self, *, validate: bool | None = None) -> MiningAlgoListResponse:
    """Query mining pool algorithms.

    References:
      - [Official docs](https://developers.binance.com/docs/mining/rest-api#acquiring-algorithm)
    """
    _Response = MiningAlgoListResponse
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/sapi/v1/mining/pub/algoList', validator=_validator, validate=validate
    )
