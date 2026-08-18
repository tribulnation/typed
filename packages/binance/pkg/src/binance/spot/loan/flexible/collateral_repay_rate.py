from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleLoanCollateralRepayRate(TypedDict):
  """The latest rate of collateral coin/loan coin when using collateral repay."""

  loanCoin: NotRequired[str]
  """Loan coin."""
  collateralCoin: NotRequired[str]
  """Collateral coin."""
  rate: NotRequired[str]
  """Collateral coin/loan coin rate."""


class CollateralRepayRate(RpcEndpoint):
  """Get the latest rate of collateral coin/loan coin when using collateral repay."""

  async def collateral_repay_rate(
    self,
    *,
    loan_coin: str,
    collateral_coin: str,
    repay_amount: float,
    validate: bool | None = None,
  ) -> FlexibleLoanCollateralRepayRate:
    """Get the latest rate of collateral coin/loan coin when using collateral repay.

    Args:
      loan_coin: Loan coin.
      collateral_coin: Collateral coin.
      repay_amount: Amount of `loanCoin` to repay. Not documented by the SDK/docs source this endpoint was authored against, but live evidence (2026-08-09) shows the venue rejects a call omitting it with `-1102 Mandatory parameter 'repayAmount' was not sent`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-crypto-loan/api/rest-api/flexible-rate#check-collateral-repay-rate)
    """
    params: dict = {
      'loanCoin': loan_coin,
      'collateralCoin': collateral_coin,
      'repayAmount': repay_amount,
    }
    _Response = FlexibleLoanCollateralRepayRate
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v2/loan/flexible/repay/rate',
      params=params,
      validator=_validator,
      validate=validate,
    )
