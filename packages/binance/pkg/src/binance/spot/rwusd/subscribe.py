from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RwusdSubscription(TypedDict):
  """Result of a RWUSD subscription."""

  success: NotRequired[bool]
  """Whether the subscription succeeded."""
  rwusdAmount: NotRequired[str]
  """Amount of RWUSD received, as a decimal string."""


class Subscribe(RpcEndpoint):
  """Subscribe RWUSD."""

  async def __call__(
    self,
    *,
    asset: Literal['USDT', 'USDC'],
    amount: float,
    validate: bool | None = None,
  ) -> RwusdSubscription:
    """Subscribe RWUSD.

    Args:
      asset: Asset to subscribe with.
      amount: Amount to subscribe with, in `asset`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#subscribe-rwusd)
    """
    params: dict = {
      'asset': asset,
      'amount': amount,
    }
    _Response = RwusdSubscription
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/rwusd/subscribe',
      params=params,
      validator=_validator,
      validate=validate,
    )
