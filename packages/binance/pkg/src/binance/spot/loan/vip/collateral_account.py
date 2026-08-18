from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanCollateralAccountCoin(TypedDict):
  """One coin balance held in a collateral account bound to a VIP loan."""

  collateralAccountId: NotRequired[str]
  """Collateral account ID."""
  collateralCoin: NotRequired[str]
  """Collateral coin held in this account."""


class VipLoanCollateralAccountPage(TypedDict):
  """Collateral account(s) bound to a VIP loan. Not observed to accept page parameters despite the `rows`/`total` shape -- see this endpoint's notes."""

  rows: NotRequired[list[VipLoanCollateralAccountCoin]]
  """Matching collateral account coin balances."""
  total: NotRequired[int]
  """Total number of matching rows."""


class CollateralAccount(RpcEndpoint):
  """Check VIP loan collateral account(s). Available to VIP users only."""

  async def collateral_account(
    self,
    *,
    order_id: int | None = None,
    collateral_account_id: int | None = None,
    validate: bool | None = None,
  ) -> VipLoanCollateralAccountPage:
    """Check VIP loan collateral account(s). Available to VIP users only.

    Args:
      order_id: Restrict results to a specific loan order.
      collateral_account_id: Restrict results to a specific collateral account.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#check-viploan-collateral-account)
    """
    params = {}
    if order_id is not None:
      params['orderId'] = order_id
    if collateral_account_id is not None:
      params['collateralAccountId'] = collateral_account_id
    _Response = VipLoanCollateralAccountPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/loan/vip/collateral/account',
      params=params,
      validator=_validator,
      validate=validate,
    )
