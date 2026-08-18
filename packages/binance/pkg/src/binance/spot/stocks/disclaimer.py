from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class EquityDisclaimerAck(TypedDict):
  """Acknowledgement of a US equity disclaimer acceptance."""

  success: NotRequired[bool]
  """`true` = acceptance recorded successfully."""


class Disclaimer(RpcEndpoint):
  """Records the user's acknowledgement and acceptance of the US equity disclaimer. This must be completed before the account can access certain US equity trading features. The acceptance is tied to the account associated with the API key."""

  async def disclaimer(self, *, validate: bool | None = None) -> EquityDisclaimerAck:
    """Records the user's acknowledgement and acceptance of the US equity disclaimer. This must be completed before the account can access certain US equity trading features. The acceptance is tied to the account associated with the API key.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-stocks-trading/api/rest-api/account#sign-us-equity-disclaimer)
    """
    _Response = EquityDisclaimerAck
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/equity/account/disclaimer',
      validator=_validator,
      validate=validate,
    )
