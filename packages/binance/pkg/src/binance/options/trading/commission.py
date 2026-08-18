from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UnderlyingCommission(TypedDict):
  """Commission rates for one underlying."""

  underlying: NotRequired[str]
  """Underlying asset."""
  makerFee: NotRequired[str]
  """Maker fee rate."""
  takerFee: NotRequired[str]
  """Taker fee rate."""


class UserCommission(TypedDict):
  """The account's option commission rates."""

  commissions: NotRequired[list[UnderlyingCommission]]
  """Commission rates, one per underlying."""


class Commission(RpcEndpoint):
  """Get the account's option commission rates."""

  async def commission(self, *, validate: bool | None = None) -> UserCommission:
    """Get the account's option commission rates.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/trade#user-commission)
    """
    _Response = UserCommission
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/eapi/v1/commission', validator=_validator, validate=validate
    )
