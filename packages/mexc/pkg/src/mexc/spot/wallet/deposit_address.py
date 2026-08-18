from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class DepositAddressItem(TypedDict):
  """Deposit address."""
  coin: str | None
  """Asset."""
  network: str | None
  """Network."""
  address: str | None
  """Deposit address."""
  memo: str | None
  """Deposit memo."""

Response: type[list[DepositAddressItem] | ErrorResponse] = list[DepositAddressItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class DepositAddress(AuthSpotMixin):
  async def deposit_address(
    self, *,
    coin: str, network: str | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> list[DepositAddressItem]:
    """Returns deposit addresses for an asset, optionally filtered by network.

    Args:
      coin: Asset for deposit address lookup.
      network: Optional deposit network filter.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#deposit-address-supporting-network)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if coin is not None:
      params['coin'] = coin
    if network is not None:
      params['network'] = network
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/deposit/address', params=params)
    return self.output(r.text, adapter, validate)
