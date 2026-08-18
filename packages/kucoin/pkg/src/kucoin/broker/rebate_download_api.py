"""`GET /api/v1/broker/api/rebase/download` — Get Broker Rebate."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerRebateDownload(TypedDict):
  """Download link for a broker rebate order file."""

  url: str
  """Pre-signed URL to the rebate order file (CSV); valid for 1 day."""


_Type = BrokerRebateDownload
adapter = validator[_Type](_Type)  # type: ignore


class RebateDownloadApi(RpcEndpoint):
  """`Get Broker Rebate` — mixed into `Broker`, the product exposing `broker.rebate_download_api`."""

  async def rebate_download_api(
    self,
    *,
    begin: str,
    end: str,
    trade_type: Literal['1', '2'],
    validate: bool | None = None,
  ) -> BrokerRebateDownload:
    """Get a download link for the API Broker program's rebate orders over a date range, filtered to spot or futures trading. Distinct from the Exchange (ND) Broker program's own rebate-download endpoint (`broker.rebate_download`) -- see notes for how the two programs differ.

    Args:
      begin: Start date, `YYYYMMDD`, e.g. `20240610`.
      end: End date, `YYYYMMDD`, e.g. `20241010`. The `begin`-`end` span may cover at most 6 months.
      trade_type: Business line to download rebates for.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'begin': begin,
      'end': end,
      'tradeType': trade_type,
    }
    return await self.authed_request(
      'GET',
      '/api/v1/broker/api/rebase/download',
      params=params,
      validator=adapter,
      validate=validate,
    )
