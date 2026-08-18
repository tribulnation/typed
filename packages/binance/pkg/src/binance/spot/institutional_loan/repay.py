from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class RiskUnitRepayResult(TypedDict):
  """The submitted risk unit repayment."""

  transactionId: NotRequired[int]
  """Transaction unique identifier."""
  amount: NotRequired[float]
  """Amount repaid."""
  repayFrom: NotRequired[Literal['MARGIN', 'SPOT']]
  """Funding source used for this repayment."""


class Repay(RpcEndpoint):
  """Perform a full or partial repayment of a risk unit's outstanding loan. Callable only with the credit account API key, which must have the `Enable Spot & Margin Trading` permission. By default (`repayFrom=MARGIN`), funds are deducted from the credit account's Margin wallet; when `repayFrom=SPOT`, funds are deducted directly from the credit account's Spot wallet."""

  async def repay(
    self,
    *,
    group_id: int,
    asset_name: str,
    amount: float,
    repay_from: Literal['MARGIN', 'SPOT'] | None = None,
    validate: bool | None = None,
  ) -> RiskUnitRepayResult:
    """Perform a full or partial repayment of a risk unit's outstanding loan. Callable only with the credit account API key, which must have the `Enable Spot & Margin Trading` permission. By default (`repayFrom=MARGIN`), funds are deducted from the credit account's Margin wallet; when `repayFrom=SPOT`, funds are deducted directly from the credit account's Spot wallet.

    Args:
      group_id: Risk unit unique identifier.
      asset_name: Asset to repay.
      amount: Amount to repay.
      repay_from: Funding source for repayment.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-institutional-loan/api/rest-api/borrow-repay#risk-unit-repay)
    """
    params: dict = {
      'groupId': group_id,
      'assetName': asset_name,
      'amount': amount,
    }
    if repay_from is not None:
      params['repayFrom'] = repay_from
    _Response = RiskUnitRepayResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/margin/loan-group/repay',
      params=params,
      validator=_validator,
      validate=validate,
    )
