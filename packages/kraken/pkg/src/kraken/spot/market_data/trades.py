"""`spot.market_data.trades` -- public Spot market data."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class TradesResult(TypedDict):
  """Trades keyed by pair, plus the polling cursor."""

  last: NotRequired[str]
  """ID to be used as `since` when polling for new trade data."""


validate_trades = validator(TradesResult)


class Trades(RpcEndpoint):
  """`spot.market_data.trades`."""

  async def trades(
    self,
    *,
    pair: str,
    asset_version: Literal[1] | None = None,
    since: str | None = None,
    count: int | None = None,
    asset_class: Literal['tokenized_asset'] | None = None,
  ) -> TradesResult:
    """Returns the last 1000 trades by default.

    Args:
      pair: Asset pair to get data for.
      asset_version: Controls whether response keys use Kraken's internal names or display names. Omitted (default): internal names are used. `assetVersion=1`: display names are used. Only `assetVersion=1` is currently supported.
      since: Return trade data since given timestamp.
      count: Return specific number of trades, up to 1000.
      asset_class: This parameter is required on requests for non-crypto pairs, i.e. use `tokenized_asset` for xstocks.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/market-data/get-recent-trades)
    """
    params: dict = {
      'pair': pair,
    }
    if asset_version is not None:
      params['assetVersion'] = asset_version
    if since is not None:
      params['since'] = since
    if count is not None:
      params['count'] = count
    if asset_class is not None:
      params['asset_class'] = asset_class

    return await self.request('/0/public/Trades', params, validator=validate_trades)
