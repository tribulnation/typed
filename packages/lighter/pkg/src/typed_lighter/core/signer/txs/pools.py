"""Public pools: create (10), update (11), mint shares (18) and burn shares (19).

Ported from lighter-go v1.0.10 `types/txtypes/{create_public_pool,update_public_pool,
mint_shares,burn_shares}.go`, validation order and messages included.
"""

from typing_extensions import Any, ClassVar
from dataclasses import dataclass

from .base import (
  ERR_FROM_ACCOUNT_INDEX_TOO_HIGH,
  ERR_FROM_ACCOUNT_INDEX_TOO_LOW,
  ERR_PUBLIC_POOL_INDEX_TOO_HIGH,
  ERR_PUBLIC_POOL_INDEX_TOO_LOW,
  FEE_TICK,
  MAX_ACCOUNT_INDEX,
  MAX_INITIAL_TOTAL_SHARES,
  MAX_MASTER_ACCOUNT_INDEX,
  MAX_POOL_SHARES_TO_MINT_OR_BURN,
  MIN_INITIAL_TOTAL_SHARES,
  MIN_POOL_SHARES_TO_MINT_OR_BURN,
  MIN_SUB_ACCOUNT_INDEX,
  SHARE_TICK,
  GoType,
  L2Tx,
  check_account,
  check_api_key,
  check_nonce_and_expiry,
  fail,
)

ERR_INVALID_OPERATOR_FEE = (
  f'PoolOperatorFee should be larger than 0 and not larger than {FEE_TICK}'
)
ERR_MIN_OPERATOR_SHARE_RATE_TOO_HIGH = (
  f'PoolMinOperatorShareRate should not be larger than {SHARE_TICK}'
)


def check_from_account(value: int, *, maximum: int = MAX_ACCOUNT_INDEX):
  """The signing account, reported under Go's `FromAccountIndex` messages."""
  check_account(
    value,
    low=ERR_FROM_ACCOUNT_INDEX_TOO_LOW,
    high=ERR_FROM_ACCOUNT_INDEX_TOO_HIGH,
    maximum=maximum,
  )


def check_operator_fee(value: int):
  """Operator fee in [0, 1_000_000]."""
  if value < 0 or value > FEE_TICK:
    fail(ERR_INVALID_OPERATOR_FEE)


def check_pool_share_account(value: int):
  """A pool account: a sub-account index (Go's message text still says -1)."""
  if value < MIN_SUB_ACCOUNT_INDEX:
    fail(ERR_PUBLIC_POOL_INDEX_TOO_LOW)
  if value > MAX_ACCOUNT_INDEX:
    fail(ERR_PUBLIC_POOL_INDEX_TOO_HIGH)


@dataclass(frozen=True, kw_only=True)
class CreatePublicPool(L2Tx):
  """`L2CreatePublicPool` (tx type 10), signed by a master account."""

  operator_fee: int
  """Operator fee in 1e-6 units."""
  initial_total_shares: int
  """Initial share supply (one share is 0.001 USDC)."""
  min_operator_share_rate: int
  """Minimum operator share in 1e-4 units (`uint16`, at most 10_000)."""

  TX_TYPE: ClassVar[int] = 10
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('operator_fee', 'OperatorFee', 'int64'),
    ('initial_total_shares', 'InitialTotalShares', 'int64'),
    ('min_operator_share_rate', 'MinOperatorShareRate', 'uint16'),
  )

  def check(self):
    """Go `L2CreatePublicPoolTxInfo.Validate`."""
    check_from_account(self.account_index, maximum=MAX_MASTER_ACCOUNT_INDEX)
    check_api_key(self.api_key_index)
    check_operator_fee(self.operator_fee)
    if self.initial_total_shares <= 0:
      fail(f'PoolInitialTotalShares should be larger than {MIN_INITIAL_TOTAL_SHARES}')
    if self.initial_total_shares > MAX_INITIAL_TOTAL_SHARES:
      fail(
        f'PoolInitialTotalShares should not be larger than {MAX_INITIAL_TOTAL_SHARES}'
      )
    if self.min_operator_share_rate > SHARE_TICK:
      fail(ERR_MIN_OPERATOR_SHARE_RATE_TOO_HIGH)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Operator fee, initial shares, minimum operator share rate."""
    return [self.operator_fee, self.initial_total_shares, self.min_operator_share_rate]

  def body_json(self) -> dict[str, Any]:
    """Operator fee, initial shares, minimum operator share rate."""
    return {
      'OperatorFee': self.operator_fee,
      'InitialTotalShares': self.initial_total_shares,
      'MinOperatorShareRate': self.min_operator_share_rate,
    }


@dataclass(frozen=True, kw_only=True)
class UpdatePublicPool(L2Tx):
  """`L2UpdatePublicPool` (tx type 11)."""

  public_pool_index: int
  """Pool account."""
  status: int
  """0 or 1."""
  operator_fee: int
  """Operator fee in 1e-6 units."""
  min_operator_share_rate: int
  """Minimum operator share in 1e-4 units (`uint16`, at most 10_000)."""

  TX_TYPE: ClassVar[int] = 11
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('public_pool_index', 'PublicPoolIndex', 'int64'),
    ('status', 'Status', 'uint8'),
    ('operator_fee', 'OperatorFee', 'int64'),
    ('min_operator_share_rate', 'MinOperatorShareRate', 'uint16'),
  )

  def check(self):
    """Go `L2UpdatePublicPoolTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    check_account(
      self.public_pool_index,
      low=ERR_PUBLIC_POOL_INDEX_TOO_LOW,
      high=ERR_PUBLIC_POOL_INDEX_TOO_HIGH,
    )
    if self.status not in (0, 1):
      fail('PoolStatus should be either 0 or 1')
    check_operator_fee(self.operator_fee)
    if self.min_operator_share_rate > SHARE_TICK:
      fail(ERR_MIN_OPERATOR_SHARE_RATE_TOO_HIGH)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Pool, status, operator fee, minimum operator share rate."""
    return [
      self.public_pool_index,
      self.status,
      self.operator_fee,
      self.min_operator_share_rate,
    ]

  def body_json(self) -> dict[str, Any]:
    """Pool, status, operator fee, minimum operator share rate."""
    return {
      'PublicPoolIndex': self.public_pool_index,
      'Status': self.status,
      'OperatorFee': self.operator_fee,
      'MinOperatorShareRate': self.min_operator_share_rate,
    }


@dataclass(frozen=True, kw_only=True)
class MintShares(L2Tx):
  """`L2MintShares` (tx type 18): buy shares of a public pool."""

  public_pool_index: int
  """Pool account (a sub-account index)."""
  share_amount: int
  """Shares to mint."""

  TX_TYPE: ClassVar[int] = 18
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('public_pool_index', 'PublicPoolIndex', 'int64'),
    ('share_amount', 'ShareAmount', 'int64'),
  )

  def check(self):
    """Go `L2MintSharesTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    check_pool_share_account(self.public_pool_index)
    if self.share_amount < MIN_POOL_SHARES_TO_MINT_OR_BURN:
      fail(
        f'PoolMintShareAmount should be larger than {MIN_POOL_SHARES_TO_MINT_OR_BURN}'
      )
    if self.share_amount > MAX_POOL_SHARES_TO_MINT_OR_BURN:
      fail(
        f'PoolMintShareAmount should not be larger than {MAX_POOL_SHARES_TO_MINT_OR_BURN}'
      )
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Pool, shares."""
    return [self.public_pool_index, self.share_amount]

  def body_json(self) -> dict[str, Any]:
    """Pool, shares."""
    return {'PublicPoolIndex': self.public_pool_index, 'ShareAmount': self.share_amount}


@dataclass(frozen=True, kw_only=True)
class BurnShares(L2Tx):
  """`L2BurnShares` (tx type 19): redeem shares of a public pool."""

  public_pool_index: int
  """Pool account (a sub-account index)."""
  share_amount: int
  """Shares to burn."""

  TX_TYPE: ClassVar[int] = 19
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('public_pool_index', 'PublicPoolIndex', 'int64'),
    ('share_amount', 'ShareAmount', 'int64'),
  )

  def check(self):
    """Go `L2BurnSharesTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    check_pool_share_account(self.public_pool_index)
    if self.share_amount < MIN_POOL_SHARES_TO_MINT_OR_BURN:
      fail(
        f'PoolBurnShareAmount should be larger than {MIN_POOL_SHARES_TO_MINT_OR_BURN}'
      )
    if self.share_amount > MAX_POOL_SHARES_TO_MINT_OR_BURN:
      fail(
        f'PoolBurnShareAmount should not be larger than {MAX_POOL_SHARES_TO_MINT_OR_BURN}'
      )
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Pool, shares."""
    return [self.public_pool_index, self.share_amount]

  def body_json(self) -> dict[str, Any]:
    """Pool, shares."""
    return {'PublicPoolIndex': self.public_pool_index, 'ShareAmount': self.share_amount}
