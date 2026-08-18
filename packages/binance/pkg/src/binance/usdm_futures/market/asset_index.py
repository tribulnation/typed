from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AssetIndex0(TypedDict):
  """Multi-Assets Mode index price and rate configuration for one asset pair."""

  symbol: str
  """Asset pair, e.g. ADAUSD."""
  time: int
  """Current time, in milliseconds since epoch."""
  index: str
  """Index price."""
  bidBuffer: NotRequired[str]
  """Bid buffer applied on top of the index."""
  askBuffer: NotRequired[str]
  """Ask buffer applied on top of the index."""
  bidRate: NotRequired[str]
  """Effective bid rate (index adjusted by bidBuffer)."""
  askRate: NotRequired[str]
  """Effective ask rate (index adjusted by askBuffer)."""
  autoExchangeBidBuffer: NotRequired[str]
  """Bid buffer used for auto-exchange."""
  autoExchangeAskBuffer: NotRequired[str]
  """Ask buffer used for auto-exchange."""
  autoExchangeBidRate: NotRequired[str]
  """Effective bid rate used for auto-exchange."""
  autoExchangeAskRate: NotRequired[str]
  """Effective ask rate used for auto-exchange."""


class AssetIndexItem(TypedDict):
  """Multi-Assets Mode index price and rate configuration for one asset pair."""

  symbol: str
  """Asset pair, e.g. ADAUSD."""
  time: int
  """Current time, in milliseconds since epoch."""
  index: str
  """Index price."""
  bidBuffer: NotRequired[str]
  """Bid buffer applied on top of the index."""
  askBuffer: NotRequired[str]
  """Ask buffer applied on top of the index."""
  bidRate: NotRequired[str]
  """Effective bid rate (index adjusted by bidBuffer)."""
  askRate: NotRequired[str]
  """Effective ask rate (index adjusted by askBuffer)."""
  autoExchangeBidBuffer: NotRequired[str]
  """Bid buffer used for auto-exchange."""
  autoExchangeAskBuffer: NotRequired[str]
  """Ask buffer used for auto-exchange."""
  autoExchangeBidRate: NotRequired[str]
  """Effective bid rate used for auto-exchange."""
  autoExchangeAskRate: NotRequired[str]
  """Effective ask rate used for auto-exchange."""


class AssetIndex(RpcEndpoint):
  """Multi-Assets Mode asset index price for an asset pair, or every asset pair when omitted."""

  async def asset_index(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> AssetIndex0 | list[AssetIndexItem]:
    """Multi-Assets Mode asset index price for an asset pair, or every asset pair when omitted.

    Args:
      symbol: Asset pair, e.g. ADAUSD. Omit to get every asset pair as an array.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#asset-index)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = AssetIndex0 | list[AssetIndexItem]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.request(
      'GET',
      '/fapi/v1/assetIndex',
      params=params,
      validator=_validator,
      validate=validate,
    )
