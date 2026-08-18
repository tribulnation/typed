from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountDepositAddress(TypedDict):
  """The sub-account's deposit address."""

  address: NotRequired[str]
  """Deposit address."""
  coin: NotRequired[str]
  """Coin the address accepts."""
  tag: NotRequired[str]
  """Address tag/memo, when the network requires one."""
  url: NotRequired[str]
  """Block explorer URL for the address."""


class DepositAddress(RpcEndpoint):
  """Get a sub-account's deposit address for one coin, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    coin: str,
    network: str | None = None,
    amount: float | None = None,
    validate: bool | None = None,
  ) -> SubAccountDepositAddress:
    """Get a sub-account's deposit address for one coin, for the master account.

    Args:
      email: Sub-account email.
      coin: Coin to get the deposit address for.
      network: Network to get the deposit address on. Networks can be found via `GET /sapi/v1/capital/deposit/address`. Defaults to the coin's default network.
      amount: Deposit amount. Required when `network` is `LIGHTNING`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#get-sub-account-deposit-address)
    """
    params: dict = {
      'email': email,
      'coin': coin,
    }
    if network is not None:
      params['network'] = network
    if amount is not None:
      params['amount'] = amount
    _Response = SubAccountDepositAddress
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/capital/deposit/subAddress',
      params=params,
      validator=_validator,
      validate=validate,
    )
