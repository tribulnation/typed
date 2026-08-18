from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class GiftCardRsaPublicKeyResponse(TypedDict):
  """RSA public key response frame. This product line wraps its business data in {code,message,data,success} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[str]
  """Response code. "000000" indicates success."""
  message: NotRequired[str]
  """Response message."""
  data: NotRequired[str]
  """Base64-encoded RSA public key, valid only for the current day."""
  success: NotRequired[bool]
  """Whether the call succeeded."""


class RsaPublicKey(RpcEndpoint):
  """Fetch the RSA public key used to encrypt a gift card redemption code before calling `spot.gift_card.redeem_code`. The key is only valid for the current day."""

  async def rsa_public_key(
    self,
    *,
    validate: bool | None = None,
  ) -> GiftCardRsaPublicKeyResponse:
    """Fetch the RSA public key used to encrypt a gift card redemption code before calling `spot.gift_card.redeem_code`. The key is only valid for the current day.

    References:
      - [Official docs](https://developers.binance.com/docs/gift_card/market-data)
    """
    _Response = GiftCardRsaPublicKeyResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/giftcard/cryptography/rsa-public-key',
      validator=_validator,
      validate=validate,
    )
