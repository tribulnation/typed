from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MiningCoin(TypedDict):
  """One mineable coin."""

  coinName: NotRequired[str]
  """Coin symbol, e.g. BTC."""
  coinId: NotRequired[int]
  """Coin identifier."""
  poolIndex: NotRequired[int]
  """Pool index."""
  algoId: NotRequired[int]
  """Algorithm identifier used to mine this coin."""
  algoName: NotRequired[str]
  """Algorithm name used to mine this coin."""


class MiningCoinListResponse(TypedDict):
  """Mining coin list response frame. This product line wraps its business data in {code,msg,data} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[int]
  """Response code. 0 indicates success."""
  msg: NotRequired[str]
  """Response message."""
  data: NotRequired[list[MiningCoin]]
  """Mineable coins."""


class CoinList(RpcEndpoint):
  """Query coins mineable through Binance's mining pool."""

  async def coin_list(self, *, validate: bool | None = None) -> MiningCoinListResponse:
    """Query coins mineable through Binance's mining pool.

    References:
      - [Official docs](https://developers.binance.com/docs/mining/rest-api#acquiring-coinname)
    """
    _Response = MiningCoinListResponse
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/sapi/v1/mining/pub/coinList', validator=_validator, validate=validate
    )
