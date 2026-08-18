from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMDownloadLink(TypedDict):
  """Status and URL of an asynchronous history export."""

  downloadId: str
  """Download task id."""
  status: Literal['completed', 'processing']
  """Export preparation status."""
  url: str
  """URL the export can be downloaded from once status is completed."""
  notified: bool
  """Whether the caller has already been notified of this export's readiness."""
  expirationTimestamp: Timestamp
  """Time after which the download link expires."""
  isExpired: NotRequired[str]
  """Whether the record is expired."""


class TransactionHistoryDownloadLink(RpcEndpoint):
  """Get the download link for a futures transaction history export previously started with coinm_futures.account.transaction_history_download_id."""

  async def transaction_history_download_link(
    self,
    *,
    download_id: str,
    validate: bool | None = None,
  ) -> CoinMDownloadLink:
    """Get the download link for a futures transaction history export previously started with coinm_futures.account.transaction_history_download_id.

    Args:
      download_id: Download id, obtained from coinm_futures.account.transaction_history_download_id.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-futures-transaction-history-download-link-by-id)
    """
    params: dict = {
      'downloadId': download_id,
    }
    _Response = CoinMDownloadLink
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/dapi/v1/income/asyn/id',
      params=params,
      validator=_validator,
      validate=validate,
    )
