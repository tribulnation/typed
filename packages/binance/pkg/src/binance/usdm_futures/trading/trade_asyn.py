from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesTradeHistoryDownloadRequest(TypedDict):
  """A newly requested futures trade history export job's download id."""

  avgCostTimestampOfLast30d: NotRequired[int]
  """Average time taken to generate a download, over the past 30 days, in milliseconds."""
  downloadId: NotRequired[str]
  """Download id for this export job, used to poll for the download link."""


class TradeAsyn(RpcEndpoint):
  """Request a download id for this account's futures trade history, generated as an asynchronous export job. The time between `startTime` and `endTime` cannot be longer than 1 year. Rate-limited to 5 requests per month, shared with the front-end download page."""

  async def trade_asyn(
    self,
    *,
    start_time: int,
    end_time: int,
    validate: bool | None = None,
  ) -> UsdMFuturesTradeHistoryDownloadRequest:
    """Request a download id for this account's futures trade history, generated as an asynchronous export job. The time between `startTime` and `endTime` cannot be longer than 1 year. Rate-limited to 5 requests per month, shared with the front-end download page.

    Args:
      start_time: Export window start, as milliseconds since epoch.
      end_time: Export window end, as milliseconds since epoch.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-trade-history)
    """
    params: dict = {
      'startTime': start_time,
      'endTime': end_time,
    }
    _Response = UsdMFuturesTradeHistoryDownloadRequest
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/fapi/v1/trade/asyn',
      params=params,
      validator=_validator,
      validate=validate,
    )
