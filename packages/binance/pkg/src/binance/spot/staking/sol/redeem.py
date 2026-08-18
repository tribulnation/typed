from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SolRedeemResult(TypedDict):
  """Result of a SOL redemption."""

  success: NotRequired[bool]
  """Whether the redemption succeeded."""
  solAmount: NotRequired[str]
  """Amount of SOL to be delivered for this redemption, as a decimal string."""
  redeemId: NotRequired[int]
  """Identifier of this redemption."""
  exchangeRate: NotRequired[str]
  """BNSOL/SOL exchange rate applied to this redemption, as a decimal string."""
  arrivalTime: NotRequired[int]
  """Millisecond epoch time the redeemed SOL is expected to arrive."""


class Redeem(RpcEndpoint):
  """Redeem BNSOL back into SOL."""

  async def __call__(
    self, *, amount: float, validate: bool | None = None
  ) -> SolRedeemResult:
    """Redeem BNSOL back into SOL.

    Args:
      amount: Amount of BNSOL to redeem. Limited to 8 decimal places.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/sol-staking#redeem-sol)
    """
    params: dict = {
      'amount': amount,
    }
    _Response = SolRedeemResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/sol-staking/sol/redeem',
      params=params,
      validator=_validator,
      validate=validate,
    )
