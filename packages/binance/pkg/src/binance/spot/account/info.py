from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AccountBalance(TypedDict):
  """One asset's balance."""

  asset: str
  """Asset symbol."""
  free: str
  """Available (unlocked) balance, as a decimal string."""
  locked: str
  """Balance locked in open orders, as a decimal string."""


class CommissionRates(TypedDict):
  """Decimal commission rates for this account."""

  maker: str
  """Maker commission rate, as a decimal string."""
  taker: str
  """Taker commission rate, as a decimal string."""
  buyer: str
  """Buyer commission rate, as a decimal string."""
  seller: str
  """Seller commission rate, as a decimal string."""


class AccountInfo(TypedDict):
  """Account trading status, commission rates, balances, and permissions."""

  makerCommission: int
  """Maker commission rate for this account, in legacy integer units; see `commissionRates.maker` for the decimal rate."""
  takerCommission: int
  """Taker commission rate for this account, in legacy integer units; see `commissionRates.taker` for the decimal rate."""
  buyerCommission: int
  """Buyer commission rate for this account, in legacy integer units. Always 0 for spot."""
  sellerCommission: int
  """Seller commission rate for this account, in legacy integer units. Always 0 for spot."""
  commissionRates: CommissionRates
  canTrade: bool
  """Whether this account is allowed to trade."""
  canWithdraw: bool
  """Whether this account is allowed to withdraw."""
  canDeposit: bool
  """Whether this account is allowed to deposit."""
  brokered: bool
  """Whether this account is a brokered (sub-)account."""
  requireSelfTradePrevention: bool
  """Whether every order from this account must specify a self-trade prevention mode."""
  preventSor: bool
  """Whether Smart Order Routing prevention is enabled for this account."""
  updateTime: int
  """Millisecond timestamp this account was last updated."""
  accountType: str
  """Account type, e.g. `SPOT`. Not a closed set — see notes."""
  balances: list[AccountBalance]
  """Asset balances held by this account (only non-zero ones when `omitZeroBalances` is true)."""
  permissions: list[
    Literal[
      'SPOT',
      'MARGIN',
      'LEVERAGED',
      'PRE_MARKET',
      'TRD_GRP_002',
      'TRD_GRP_003',
      'TRD_GRP_004',
      'TRD_GRP_005',
      'TRD_GRP_006',
      'TRD_GRP_007',
      'TRD_GRP_008',
      'TRD_GRP_009',
      'TRD_GRP_010',
      'TRD_GRP_011',
      'TRD_GRP_012',
      'TRD_GRP_013',
      'TRD_GRP_014',
      'TRD_GRP_015',
      'TRD_GRP_016',
      'TRD_GRP_017',
      'TRD_GRP_018',
      'TRD_GRP_019',
      'TRD_GRP_020',
      'TRD_GRP_021',
      'TRD_GRP_022',
      'TRD_GRP_023',
      'TRD_GRP_024',
      'TRD_GRP_025',
    ]
  ]
  """Account and symbol permission types held by this account."""
  uid: int
  """Binance user id."""


class Info(RpcEndpoint):
  """Account information"""

  async def info(
    self,
    *,
    omit_zero_balances: bool | None = None,
    validate: bool | None = None,
  ) -> AccountInfo:
    """Get current account information: trading permissions, commission rates, balances, and account status.

    Args:
      omit_zero_balances: When true, only non-zero asset balances are included in `balances`.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params = {}
    if omit_zero_balances is not None:
      params['omitZeroBalances'] = omit_zero_balances
    _Response = AccountInfo
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/api/v3/account', params=params, validator=_validator, validate=validate
    )
