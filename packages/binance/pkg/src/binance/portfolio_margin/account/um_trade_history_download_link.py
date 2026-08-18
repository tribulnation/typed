from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmUmFuturesTradeDownloadLinkById(TypedDict):
  """Get UM futures trade download link by Id."""

  downloadId: NotRequired[str]
  """Download ID."""
  status: NotRequired[str]
  """Enum：completed，processing."""
  url: NotRequired[str]
  """The link is mapped to download id."""
  s3Link: NotRequired[str]
  """S3 Link."""
  notified: NotRequired[bool]
  """ignore."""
  expirationTimestamp: NotRequired[int]
  """The link would expire after this timestamp."""
  isExpired: NotRequired[str]
  """Is Expired."""


class UmTradeHistoryDownloadLink(RpcEndpoint):
  """Get UM Futures Trade Download Link by Id"""

  async def um_trade_history_download_link(
    self,
    *,
    download_id: str,
    validate: bool | None = None,
  ) -> PmUmFuturesTradeDownloadLinkById:
    """Get UM futures trade download link by Id.

    Args:
      download_id: get by download id api.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-futures-trade-download-link-by-id)
    """
    params: dict = {
      'downloadId': download_id,
    }
    _Response = PmUmFuturesTradeDownloadLinkById
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/trade/asyn/id',
      params=params,
      validator=_validator,
      validate=validate,
    )
