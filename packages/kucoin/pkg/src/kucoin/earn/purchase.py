"""`POST /api/v1/earn/orders` — Purchase."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class PurchaseRequest(TypedDict):
  productId: str
  """Product id to subscribe to, as returned by one of the `Get *Products` endpoints."""
  amount: str
  """Amount to subscribe."""
  accountType: Literal['MAIN', 'TRADE']
  """Source account to draw funds from."""


class PurchaseResult(TypedDict):
  orderId: str
  """New holding id -- the identifier used by `earn.redeem_preview`/`earn.redeem`/`earn.account_holding`."""
  orderTxId: str
  """Subscription order transaction id."""


_Type = PurchaseResult
adapter = validator[_Type](_Type)  # type: ignore


class Purchase(RpcEndpoint):
  """`Purchase` — mixed into `Earn`, the product exposing `earn.purchase`."""

  async def purchase(
    self,
    purchase_request: PurchaseRequest,
    *,
    validate: bool | None = None,
  ) -> PurchaseResult:
    """Subscribe to an Earn product -- savings, promotion, staking, KCS-staking or ETH-staking -- moving funds from the given account into a new holding.

    Args:
      purchase_request: Purchase parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/earn/orders',
      json=purchase_request,
      validator=adapter,
      validate=validate,
    )
