from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BfusdRedemption(TypedDict):
  """Result of a BFUSD redemption."""

  success: NotRequired[bool]
  """Whether the redemption succeeded."""
  receiveAmount: NotRequired[str]
  """Amount of USDT credited, as a decimal string."""
  fee: NotRequired[str]
  """Redemption fee, as a decimal string."""
  arrivalTime: NotRequired[int]
  """Millisecond epoch time the credited amount is expected to arrive."""


class Redeem(RpcEndpoint):
  """Redeem BFUSD to USDT."""

  async def __call__(
    self,
    *,
    amount: float,
    type: Literal['FAST', 'STANDARD'],
    validate: bool | None = None,
  ) -> BfusdRedemption:
    """Redeem BFUSD to USDT.

    Args:
      amount: Amount to redeem, in BFUSD.
      type: Redemption type. Defaults to `STANDARD`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#redeem-bfusd)
    """
    params: dict = {
      'amount': amount,
      'type': type,
    }
    _Response = BfusdRedemption
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/bfusd/redeem',
      params=params,
      validator=_validator,
      validate=validate,
    )
