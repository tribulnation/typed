from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AssetDividendRecord(TypedDict):
  """A single dividend distribution."""

  id: int
  """Record ID."""
  amount: str
  """Distributed amount."""
  asset: str
  """Distributed asset."""
  divTime: int
  """Distribution time, as milliseconds since epoch."""
  enInfo: str
  """Human-readable description of the distribution."""
  tranId: int
  """Transaction ID."""


class AssetDividendRecords(TypedDict):
  """Page of asset dividend records."""

  rows: list[AssetDividendRecord]
  """Matching dividend records."""
  total: int
  """Total number of matching records."""


class Dividend(RpcEndpoint):
  """Query asset dividend records, e.g. staking/airdrop distributions credited to the account. `startTime`/`endTime` cannot span more than 180 days."""

  async def __call__(
    self,
    *,
    asset: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> AssetDividendRecords:
    """Query asset dividend records, e.g. staking/airdrop distributions credited to the account. `startTime`/`endTime` cannot span more than 180 days.

    Args:
      asset: Asset to query. Returns every asset when omitted.
      start_time: Query period start, as milliseconds since epoch.
      end_time: Query period end, as milliseconds since epoch.
      limit: Number of records to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#asset-dividend-record)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    _Response = AssetDividendRecords
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/asset/assetDividend',
      params=params,
      validator=_validator,
      validate=validate,
    )
