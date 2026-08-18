"""`GET /api/v3/broker/nd/rebate/download` — Get Broker RebateV3."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerRebateDownload(TypedDict):
  """Download link for a broker rebate order file."""

  url: str
  """Download link for the rebate order file (CSV)."""


_Type = BrokerRebateDownload
adapter = validator[_Type](_Type)  # type: ignore


class RebateDownloadV3(RpcEndpoint):
  """`Get Broker RebateV3` — mixed into `Broker`, the product exposing `broker.rebate_download_v3`."""

  async def rebate_download_v3(
    self,
    *,
    begin: str,
    end: str,
    trade_type: Literal['SPOT', 'FUTURE'],
    x_tenant: str,
    validate: bool | None = None,
  ) -> BrokerRebateDownload:
    """Get a download link for the Exchange (ND) Broker's rebate orders over a date range, filtered to spot or futures trading -- the v3 successor to `broker.rebate_download` (v1), on the same host and requiring the caller's tenant name. Sits alongside the v1 endpoint rather than replacing it; the two are specced independently since KuCoin has not deprecated v1.

    Args:
      begin: Start date. KuCoin's docs give no format here (unlike v1's explicit `YYYYMMDD`); assumed the same, unconfirmed.
      end: End date. KuCoin's docs give no format here (unlike v1's explicit `YYYYMMDD`); assumed the same, unconfirmed.
      trade_type: Business line to download rebates for.
      x_tenant: Broker tenant name identifying which Exchange (ND) Broker this request is for.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'begin': begin,
      'end': end,
      'tradeType': trade_type,
    }
    headers: dict = {
      'x-tenant': x_tenant,
    }
    return await self.authed_request(
      'GET',
      '/api/v3/broker/nd/rebate/download',
      params=params,
      headers=headers,
      validator=adapter,
      validate=validate,
    )
