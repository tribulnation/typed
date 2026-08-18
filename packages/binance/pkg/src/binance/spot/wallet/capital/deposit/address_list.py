from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DepositAddressEntry(TypedDict):
  """One deposit address for a coin on a network."""

  coin: str
  """Coin this address accepts."""
  address: str
  """Deposit address."""
  isDefault: int
  """Whether this is the coin's default network address: `1` if default, `0` otherwise."""


class AddressList(RpcEndpoint):
  """Fetch every deposit address on file for a coin, across every network it's been used with. Unlike `capital.deposit.address`, which returns one address, this returns the full list."""

  async def address_list(
    self,
    *,
    coin: str,
    network: str | None = None,
    validate: bool | None = None,
  ) -> list[DepositAddressEntry]:
    """Fetch every deposit address on file for a coin, across every network it's been used with. Unlike `capital.deposit.address`, which returns one address, this returns the full list.

    Args:
      coin: Coin to fetch deposit addresses for.
      network: Network to filter the returned addresses by.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#fetch-deposit-address-list-with-network)
    """
    params: dict = {
      'coin': coin,
    }
    if network is not None:
      params['network'] = network
    _Response = list[DepositAddressEntry]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/capital/deposit/address/list',
      params=params,
      validator=_validator,
      validate=validate,
    )
