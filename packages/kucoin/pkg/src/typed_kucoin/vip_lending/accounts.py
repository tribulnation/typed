"""`GET /api/v1/otc-loan/accounts` — Get Accounts."""

from typed_core.validation import TypedDict, validator
from typed_kucoin.core import RpcEndpoint


class LoanAccount(TypedDict):
  """One account (master or sub-account) participating in a VIP loan's margin pool."""

  uid: str
  """Account UID."""
  marginCcy: str
  """Margin currency."""
  marginQty: str
  """Maintenance quantity, calculated with `marginFactor`."""
  marginFactor: str
  """Margin coefficient."""
  accountType: str
  """Account type, for example `TRADE` (trading account) or `CONTRACT` (futures account)."""
  isParent: bool
  """Whether this is the master account."""


adapter = validator(list[LoanAccount])


class Accounts(RpcEndpoint):
  """`Get Accounts` — mixed into `VipLending`, the product exposing
  `vip_lending.accounts`."""

  async def accounts(self, *, validate: bool | None = None) -> list[LoanAccount]:
    """List the accounts participating in the authenticated VIP loan's margin pool.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'GET', '/api/v1/otc-loan/accounts', validator=adapter, validate=validate
    )
