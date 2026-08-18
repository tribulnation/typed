from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class GenerateDepositAddressItem(TypedDict):
  """Deposit address."""
  coin: str | None
  """Asset."""
  network: str | None
  """Network."""
  address: str | None
  """Deposit address."""
  tag: NotRequired[str | None]
  """Deposit address tag."""
  memo: NotRequired[str | None]
  """Deposit memo."""

Response: type[list[GenerateDepositAddressItem] | ErrorResponse] = list[GenerateDepositAddressItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class GenerateDepositAddress(AuthSpotMixin):
  async def generate_deposit_address(
    self, *,
    coin: str, network: str, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> list[GenerateDepositAddressItem]:
    """Creates or returns a deposit address for a coin and network.

    Args:
      coin: Asset for the deposit address.
      network: Deposit network.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#generate-deposit-address-supporting-network)
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
    r = await self.signed_request('POST', '/api/v3/capital/deposit/address', params=params)
    return self.output(r.text, adapter, validate)
