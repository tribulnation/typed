from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class GiftCardCode(TypedDict):
  """The newly created gift card."""

  referenceNo: NotRequired[str]
  """Gift card reference number, used to verify the card."""
  code: NotRequired[str]
  """Redemption code. Keep confidential -- anyone holding it can redeem the card."""
  expiredTime: NotRequired[int]
  """Millisecond epoch expiration timestamp."""


class GiftCardCodeResponse(TypedDict):
  """Gift card creation response frame. This product line wraps its business data in {code,message,data,success} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[str]
  """Response code. "000000" indicates success."""
  message: NotRequired[str]
  """Response message."""
  data: NotRequired[GiftCardCode]
  success: NotRequired[bool]
  """Whether the call succeeded."""


class CreateCode(RpcEndpoint):
  """Create a single-token Binance Gift Card: pay and redeem in the same `token`."""

  async def create_code(
    self,
    *,
    token: str,
    amount: float,
    validate: bool | None = None,
  ) -> GiftCardCodeResponse:
    """Create a single-token Binance Gift Card: pay and redeem in the same `token`.

    Args:
      token: Token the gift card is denominated in and redeems into.
      amount: Amount of `token` to fund the card with.

    References:
      - [Official docs](https://developers.binance.com/docs/gift_card/market-data)
    """
    params: dict = {
      'token': token,
      'amount': amount,
    }
    _Response = GiftCardCodeResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/giftcard/createCode',
      params=params,
      validator=_validator,
      validate=validate,
    )
