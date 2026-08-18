from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProRepayFuturesNegativeBalance(TypedDict):
  """Repay futures negative balance result."""

  msg: NotRequired[str]
  """Result message."""


class RepayFuturesNegativeBalance(RpcEndpoint):
  """Repay futures Negative Balance"""

  async def repay_futures_negative_balance(
    self,
    *,
    from_: Literal['SPOT', 'MARGIN'] | None = None,
    validate: bool | None = None,
  ) -> PmProRepayFuturesNegativeBalance:
    """Repay futures Negative Balance.

    Args:
      from_: Source account to repay from.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#repay-futures-negative-balance)
    """
    params = {}
    if from_ is not None:
      params['from'] = from_
    _Response = PmProRepayFuturesNegativeBalance
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/portfolio/repay-futures-negative-balance',
      params=params,
      validator=_validator,
      validate=validate,
    )
