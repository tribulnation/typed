from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesTradeHistoryDownloadLink(TypedDict):
  """Status and download link for a futures trade history export job."""

  downloadId: NotRequired[str]
  """Download id this status/link corresponds to."""
  status: NotRequired[Literal['completed', 'processing']]
  """Export job status."""
  url: NotRequired[str]
  """Download link for the export, once `status` is `completed`."""
  notified: NotRequired[bool]
  """Reserved field; not meaningful to callers."""
  expirationTimestamp: NotRequired[int]
  """Time the download link expires, as milliseconds since epoch."""
  isExpired: NotRequired[str]
  """Whether the download link has already expired."""


class TradeAsynId(RpcEndpoint):
  """Get the futures trade history download link for a download id previously obtained from `usdm_futures.trading.trade_asyn`. The link expires 7 days after it becomes available."""

  async def trade_asyn_id(
    self,
    *,
    download_id: str,
    validate: bool | None = None,
  ) -> UsdMFuturesTradeHistoryDownloadLink:
    """Get the futures trade history download link for a download id previously obtained from `usdm_futures.trading.trade_asyn`. The link expires 7 days after it becomes available.

    Args:
      download_id: Download id, obtained from `usdm_futures.trading.trade_asyn`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-trade-download-link-by-id)
    """
    params: dict = {
      'downloadId': download_id,
    }
    _Response = UsdMFuturesTradeHistoryDownloadLink
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/fapi/v1/trade/asyn/id',
      params=params,
      validator=_validator,
      validate=validate,
    )
