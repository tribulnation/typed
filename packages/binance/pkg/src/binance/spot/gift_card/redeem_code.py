from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class GiftCardRedemption(TypedDict):
  """The redeemed value, credited to the funding wallet."""

  referenceNo: NotRequired[str]
  """Gift card reference number."""
  identityNo: NotRequired[str]
  """Redemption identity number."""
  token: NotRequired[str]
  """Token credited."""
  amount: NotRequired[str]
  """Amount credited."""


class GiftCardRedemptionResponse(TypedDict):
  """Gift card redemption response frame. This product line wraps its business data in {code,message,data,success} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[str]
  """Response code. "000000" indicates success."""
  message: NotRequired[str]
  """Response message."""
  data: NotRequired[GiftCardRedemption]
  success: NotRequired[bool]
  """Whether the call succeeded."""


class RedeemCode(RpcEndpoint):
  """Redeem a Binance Gift Card, depositing its value into this account's funding wallet."""

  async def redeem_code(
    self,
    *,
    code: str,
    external_uid: str | None = None,
    validate: bool | None = None,
  ) -> GiftCardRedemptionResponse:
    """Redeem a Binance Gift Card, depositing its value into this account's funding wallet.

    Args:
      code: Redemption code, plaintext or RSA-encrypted with `spot.gift_card.rsa_public_key`.
      external_uid: Caller-supplied external user identifier, echoed back for reconciliation.

    References:
      - [Official docs](https://developers.binance.com/docs/gift_card/market-data)
    """
    params: dict = {
      'code': code,
    }
    if external_uid is not None:
      params['externalUid'] = external_uid
    _Response = GiftCardRedemptionResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/giftcard/redeemCode',
      params=params,
      validator=_validator,
      validate=validate,
    )
