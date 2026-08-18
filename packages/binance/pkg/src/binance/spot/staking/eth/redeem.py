from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class EthRedeemResult(TypedDict):
  """Result of an ETH redemption."""

  success: NotRequired[bool]
  """Whether the redemption succeeded."""
  ethAmount: NotRequired[str]
  """Amount of ETH to be delivered for this redemption, as a decimal string."""
  redeemId: NotRequired[int]
  """Identifier of this redemption."""
  conversionRatio: NotRequired[str]
  """Conversion ratio applied to this redemption, as a decimal string."""
  arrivalTime: NotRequired[int]
  """Millisecond epoch time the redeemed ETH is expected to arrive."""


class Redeem(RpcEndpoint):
  """Redeem WBETH or BETH back into ETH."""

  async def __call__(
    self,
    *,
    amount: float,
    asset: Literal['WBETH', 'BETH'] | None = None,
    validate: bool | None = None,
  ) -> EthRedeemResult:
    """Redeem WBETH or BETH back into ETH.

    Args:
      amount: Amount to redeem, documented in BETH terms (see notes). Limited to 8 decimal places.
      asset: Asset to redeem from.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/eth-staking#redeem-eth)
    """
    params: dict = {
      'amount': amount,
    }
    if asset is not None:
      params['asset'] = asset
    _Response = EthRedeemResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/eth-staking/eth/redeem',
      params=params,
      validator=_validator,
      validate=validate,
    )
