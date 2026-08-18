from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleRedemption(TypedDict):
  """Result of a flexible product redemption."""

  redeemId: NotRequired[int]
  """Identifier of the created redemption."""
  success: NotRequired[bool]
  """Whether the redemption succeeded."""


class Redeem(RpcEndpoint):
  """Redeem an amount (or the full position) from a Simple Earn flexible product."""

  async def __call__(
    self,
    *,
    product_id: str,
    redeem_all: bool | None = None,
    amount: str | None = None,
    dest_account: Literal['SPOT', 'FUND'] | None = None,
    validate: bool | None = None,
  ) -> FlexibleRedemption:
    """Redeem an amount (or the full position) from a Simple Earn flexible product.

    Args:
      product_id: Flexible product identifier to redeem from.
      redeem_all: Redeem the entire position. When `false`, `amount` is required.
      amount: Amount to redeem, as a decimal string. Mandatory when `redeemAll` is `false`.
      dest_account: Wallet to credit the redeemed amount to.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#redeem-flexible-product)
    """
    params: dict = {
      'productId': product_id,
    }
    if redeem_all is not None:
      params['redeemAll'] = redeem_all
    if amount is not None:
      params['amount'] = amount
    if dest_account is not None:
      params['destAccount'] = dest_account
    _Response = FlexibleRedemption
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/simple-earn/flexible/redeem',
      params=params,
      validator=_validator,
      validate=validate,
    )
