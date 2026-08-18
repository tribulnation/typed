"""`GET /api/v1/accounts/transferable` — Get Transfer Quotas."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class TransferQuota(TypedDict):
  currency: str
  """Currency, echoed back."""
  balance: str
  """Total funds in the account."""
  available: str
  """Funds available to withdraw or trade."""
  holds: str
  """Funds on hold (not available for use)."""
  transferable: str
  """Funds available to transfer out of this account/currency."""


_Type = TransferQuota
adapter = validator[_Type](_Type)  # type: ignore


class Quotas(RpcEndpoint):
  """`Get Transfer Quotas` — mixed into `Transfer`, the product exposing `account.transfer.quotas`."""

  async def quotas(
    self,
    *,
    currency: str,
    type: Literal[
      'MAIN', 'TRADE', 'MARGIN', 'ISOLATED', 'OPTION', 'MARGIN_V2', 'ISOLATED_V2'
    ],
    tag: str | None = None,
    validate: bool | None = None,
  ) -> TransferQuota:
    """Report the transferable balance of one currency in one specified account type -- total balance, available amount, held amount, and the amount actually eligible to transfer out. A read: it reports a balance snapshot, it does not move funds.

    Args:
      currency: Currency code to query, e.g. `BTC`, `ETH`, `USDT`.
      type: Account type to query.
      tag: Trading pair; required when `type` is `ISOLATED` or `ISOLATED_V2`, must not be passed for other account types, e.g. `ETH-USDT`, `KCS-USDT`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'currency': currency,
      'type': type,
    }
    if tag is not None:
      params['tag'] = tag
    return await self.authed_request(
      'GET',
      '/api/v1/accounts/transferable',
      params=params,
      validator=adapter,
      validate=validate,
    )
