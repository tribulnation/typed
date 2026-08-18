from json import dumps
from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RemoveFuturesIpWhitelistsResult(TypedDict):
  """Result of removing the IP address(es) from the whitelist."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""


class FuturesIpWhitelistRemove(RpcEndpoint):
  """Remove IP address(es) from the FAPI-MM or FSTREAM-MM futures whitelist endpoint."""

  async def futures_ip_whitelist_remove(
    self,
    *,
    endpoint: Literal['FAPI-MM', 'FSTREAM-MM'],
    ip_addresses: list[str],
    validate: bool | None = None,
  ) -> RemoveFuturesIpWhitelistsResult:
    """Remove IP address(es) from the FAPI-MM or FSTREAM-MM futures whitelist endpoint.

    Args:
      endpoint: Futures IP whitelist endpoint to remove the IP address(es) from.
      ip_addresses: IP addresses to remove from the whitelist.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-vip-service/api/rest-api/~#remove-futures-ip-whitelists)
    """
    params: dict = {
      'endpoint': endpoint,
      'ipAddresses': dumps(ip_addresses, separators=(',', ':')),
    }
    _Response = RemoveFuturesIpWhitelistsResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/sapi/v1/vip/vip-portal/futures/ip-whitelists',
      params=params,
      validator=_validator,
      validate=validate,
    )
