"""`POST /api/v3/redeem` — Redeem."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class RedeemRequest(TypedDict):
  currency: str
  """Currency of the purchase order, e.g. `BTC`, `ETH`, `USDT`."""
  size: str
  """Amount to redeem."""
  purchaseOrderNo: str
  """Id of the purchase order being redeemed."""


class RedeemResult(TypedDict):
  orderNo: str
  """Unique id assigned to the new redeem order."""


_Type = RedeemResult
adapter = validator[_Type](_Type)  # type: ignore


class Redeem(RpcEndpoint):
  """`Redeem` — mixed into `Credit`, the product exposing `margin.credit.redeem`."""

  async def redeem(
    self,
    redeem_request: RedeemRequest,
    *,
    validate: bool | None = None,
  ) -> RedeemResult:
    """Redeem (pull back) a margin credit purchase order, in full or in part.

    Args:
      redeem_request: Redeem parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/redeem',
      json=redeem_request,
      validator=adapter,
      validate=validate,
    )
