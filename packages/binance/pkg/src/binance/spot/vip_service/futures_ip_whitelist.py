from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FuturesIpWhitelistEntry(TypedDict):
  """Whitelist status for one futures endpoint."""

  endpoint: NotRequired[str]
  """Futures IP whitelist endpoint this entry belongs to."""
  totalConnectionQuota: NotRequired[int]
  """Maximum number of concurrent connections allowed for this endpoint."""
  connectionCount: NotRequired[int]
  """Current number of live connections for this endpoint."""
  ipLimit: NotRequired[int]
  """Maximum number of IP addresses that can be whitelisted for this endpoint."""
  addIpCount: NotRequired[int]
  """Number of IP addresses currently whitelisted for this endpoint."""
  ipConnections: NotRequired[dict[str, int]]
  """Per-IP connection status, keyed by IP address."""


class FuturesIpWhitelistResult(TypedDict):
  """Futures IP whitelist entries."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""
  data: NotRequired[list[FuturesIpWhitelistEntry]]
  """One entry per queried whitelist endpoint."""


class FuturesIpWhitelist(RpcEndpoint):
  """Query the futures IP whitelist for each endpoint, including per-IP connection status and connection counts."""

  async def futures_ip_whitelist(
    self,
    *,
    endpoint: Literal['FAPI-MM', 'FSTREAM-MM'] | None = None,
    validate: bool | None = None,
  ) -> FuturesIpWhitelistResult:
    """Query the futures IP whitelist for each endpoint, including per-IP connection status and connection counts.

    Args:
      endpoint: Futures IP whitelist endpoint to filter by. Omit to return all endpoints.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-vip-service/api/rest-api/~#query-futures-ip-whitelists)
    """
    params = {}
    if endpoint is not None:
      params['endpoint'] = endpoint
    _Response = FuturesIpWhitelistResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/vip/vip-portal/futures/ip-whitelists',
      params=params,
      validator=_validator,
      validate=validate,
    )
