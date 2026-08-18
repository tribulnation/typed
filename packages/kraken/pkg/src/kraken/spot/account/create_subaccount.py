"""`spot.account.create_subaccount` -- private Spot endpoint."""

from typed_core.validation import validator
from ...core.endpoint.rpc import RpcEndpoint


validate_create_subaccount = validator(bool)


class CreateSubaccount(RpcEndpoint):
  """`spot.account.create_subaccount`."""

  async def create_subaccount(self, *, username: str, email: str) -> bool:
    """Create a trading subaccount. Must be called using an API key from the master account. Subaccounts are currently only available to institutional clients; contact your Account Manager for details.

    **API Key Permissions Required:** `Funds permissions - Withdraw`

    Args:
      username: Username for the subaccount.
      email: Email address for the subaccount.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/subaccounts/create-subaccount)
    """
    data: dict = {
      'username': username,
      'email': email,
    }

    return await self.authed_request(
      '/0/private/CreateSubaccount', data, validator=validate_create_subaccount
    )
