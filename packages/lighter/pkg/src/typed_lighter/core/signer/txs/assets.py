"""Asset movements: transfer (12), withdraw (13), stake (35) and unstake (36).

Ported from lighter-go v1.0.10 `types/txtypes/{transfer,withdraw,stake_assets,
unstake_assets}.go`, validation order and messages included.
"""

from typing_extensions import Any, ClassVar
from dataclasses import dataclass

from .. import field
from .base import (
  ERR_FROM_ACCOUNT_INDEX_TOO_HIGH,
  ERR_FROM_ACCOUNT_INDEX_TOO_LOW,
  ERR_PUBLIC_POOL_INDEX_TOO_HIGH,
  ERR_PUBLIC_POOL_INDEX_TOO_LOW,
  ERR_TO_ACCOUNT_INDEX_TOO_HIGH,
  ERR_TO_ACCOUNT_INDEX_TOO_LOW,
  MAX_ACCOUNT_INDEX,
  MAX_STAKING_SHARES_TO_MINT_OR_BURN,
  MAX_TRANSFER_AMOUNT,
  MAX_WITHDRAWAL_AMOUNT,
  MIN_STAKING_SHARES_TO_MINT_OR_BURN,
  MIN_SUB_ACCOUNT_INDEX,
  GoType,
  L2Tx,
  b64,
  check_account,
  check_api_key,
  check_asset,
  check_nonce_and_expiry,
  check_route,
  fail,
  go_json,
  hex10,
)

ROUTE_PERPS, ROUTE_SPOT = 0, 1
"""Asset route types: which side of an account (perps or spot) an amount moves from/to."""

TEMPLATE_TRANSFER = (
  'Transfer\n\nnonce: {}\nfrom: {} (route {})\napi key: {}\nto: {} (route {})\nasset: {}\n'
  'amount: {}\nfee: {}\nchainId: {}\nmemo: {}\nOnly sign this message for a trusted client!'
)
"""Go `TemplateTransfer`."""


def split_uint64(value: int) -> list[int]:
  """Low and high 32 bits of `uint64(value)`, as transfers and withdrawals hash an amount."""
  unsigned = value & field.MASK64
  return [unsigned & 0xFFFFFFFF, unsigned >> 32]


def check_from_account(value: int):
  """The signing account, reported under Go's `FromAccountIndex` messages."""
  check_account(
    value, low=ERR_FROM_ACCOUNT_INDEX_TOO_LOW, high=ERR_FROM_ACCOUNT_INDEX_TOO_HIGH
  )


@dataclass(frozen=True, kw_only=True)
class Transfer(L2Tx):
  """`L2Transfer` (tx type 12): move an asset between accounts or between perps and spot.

  The 32-byte `memo` is part of the L1 message and of `tx_info` (as a JSON array of 32
  numbers), but not of the L2 hash. Needs an L1 signature unless both accounts share the
  same master account.
  """

  to_account_index: int
  """Receiving account."""
  asset_index: int
  """Asset id in [1, 62] (3 is USDC)."""
  from_route_type: int
  """`ROUTE_PERPS` or `ROUTE_SPOT` on the sending side."""
  to_route_type: int
  """`ROUTE_PERPS` or `ROUTE_SPOT` on the receiving side."""
  amount: int
  """Amount in the asset's smallest unit."""
  usdc_fee: int
  """Transfer fee in 1e-6 USDC."""
  memo: bytes = bytes(32)
  """Exactly 32 bytes."""

  TX_TYPE: ClassVar[int] = 12
  ACCOUNT_KEY: ClassVar[str] = 'FromAccountIndex'
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('to_account_index', 'ToAccountIndex', 'int64'),
    ('asset_index', 'AssetIndex', 'int16'),
    ('from_route_type', 'FromRouteType', 'uint8'),
    ('to_route_type', 'ToRouteType', 'uint8'),
    ('amount', 'Amount', 'int64'),
    ('usdc_fee', 'USDCFee', 'int64'),
  )

  def check_types(self):
    """Go integer type checks; `Memo` is a Go `[32]byte`."""
    super().check_types()
    if not isinstance(self.memo, bytes) or len(self.memo) != 32:
      fail(f'Memo does not fit [32]byte: {self.memo!r}')

  def check(self):
    """Go `L2TransferTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    check_account(
      self.to_account_index,
      low=ERR_TO_ACCOUNT_INDEX_TOO_LOW,
      high=ERR_TO_ACCOUNT_INDEX_TOO_HIGH,
    )
    check_asset(self.asset_index)
    check_route(self.from_route_type)
    check_route(self.to_route_type)
    if self.amount <= 0:
      fail('TransferAmount should be larger than 1')
    if self.amount > MAX_TRANSFER_AMOUNT:
      fail(f'TransferAmount should not be larger than {MAX_TRANSFER_AMOUNT}')
    if self.usdc_fee < 0:
      fail('TransferFee should not be negative')
    if self.usdc_fee > MAX_TRANSFER_AMOUNT:
      fail(f'TransferFee should not be larger than {MAX_TRANSFER_AMOUNT}')
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Receiver, asset, routes, and amount and fee split into `uint64` halves (no memo)."""
    return [
      self.to_account_index,
      self.asset_index,
      self.from_route_type,
      self.to_route_type,
      *split_uint64(self.amount),
      *split_uint64(self.usdc_fee),
    ]

  def body_json(self) -> dict[str, Any]:
    """Receiver, asset, routes, amount, fee, memo."""
    return {
      'ToAccountIndex': self.to_account_index,
      'AssetIndex': self.asset_index,
      'FromRouteType': self.from_route_type,
      'ToRouteType': self.to_route_type,
      'Amount': self.amount,
      'USDCFee': self.usdc_fee,
      'Memo': list(self.memo),
    }

  def tx_info(self, sig: bytes, *, l1_sig: str = '') -> str:
    """Go's JSON, with `L1Sig` after `Sig`."""
    return go_json(
      {
        'FromAccountIndex': self.account_index,
        'ApiKeyIndex': self.api_key_index,
        **self.body_json(),
        'ExpiredAt': self.expired_at,
        'Nonce': self.nonce,
        'Sig': b64(sig),
        'L1Sig': l1_sig,
        'L2TxAttributes': self.attributes.to_json(),
      }
    )

  def l1_message(self, chain_id: int) -> str:
    """Go `GetL1SignatureBody(chainId)`; the memo appears as 64 hex digits."""
    return TEMPLATE_TRANSFER.format(
      hex10(self.nonce),
      hex10(self.account_index),
      hex10(self.from_route_type),
      hex10(self.api_key_index),
      hex10(self.to_account_index),
      hex10(self.to_route_type),
      hex10(self.asset_index),
      hex10(self.amount),
      hex10(self.usdc_fee),
      hex10(chain_id),
      self.memo.hex(),
    )


@dataclass(frozen=True, kw_only=True)
class Withdraw(L2Tx):
  """`L2Withdraw` (tx type 13): withdraw to the account's own L1 address (secure withdrawal)."""

  asset_index: int
  """Asset id in [1, 62]."""
  route_type: int
  """`ROUTE_PERPS` or `ROUTE_SPOT`."""
  amount: int
  """Amount in the asset's smallest unit (`uint64`)."""

  TX_TYPE: ClassVar[int] = 13
  ACCOUNT_KEY: ClassVar[str] = 'FromAccountIndex'
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('asset_index', 'AssetIndex', 'int16'),
    ('route_type', 'RouteType', 'uint8'),
    ('amount', 'Amount', 'uint64'),
  )

  def check(self):
    """Go `L2WithdrawTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    check_asset(self.asset_index)
    check_route(self.route_type)
    if self.amount == 0:
      fail('WithdrawalAmount should be larger than 1')
    if self.amount > MAX_WITHDRAWAL_AMOUNT:
      fail(f'WithdrawalAmount should not be larger than {MAX_WITHDRAWAL_AMOUNT}')
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Asset, route, and the amount split into `uint64` halves."""
    return [self.asset_index, self.route_type, *split_uint64(self.amount)]

  def body_json(self) -> dict[str, Any]:
    """Asset, route, amount."""
    return {
      'AssetIndex': self.asset_index,
      'RouteType': self.route_type,
      'Amount': self.amount,
    }


@dataclass(frozen=True, kw_only=True)
class StakeAssets(L2Tx):
  """`L2StakeAssets` (tx type 35): buy shares of a staking pool."""

  staking_pool_index: int
  """Staking pool account (a sub-account index)."""
  share_amount: int
  """Shares to stake."""

  TX_TYPE: ClassVar[int] = 35
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('staking_pool_index', 'StakingPoolIndex', 'int64'),
    ('share_amount', 'ShareAmount', 'int64'),
  )

  def check(self):
    """Go `L2StakeAssetsTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    if self.staking_pool_index < MIN_SUB_ACCOUNT_INDEX:
      fail(f'StakingPoolIndex should not be less than {MIN_SUB_ACCOUNT_INDEX}')
    if self.staking_pool_index > MAX_ACCOUNT_INDEX:
      fail(f'StakingPoolIndex should not be larger than {MAX_ACCOUNT_INDEX}')
    if self.share_amount < MIN_STAKING_SHARES_TO_MINT_OR_BURN:
      fail(
        f'StakeAssetsAmount should be larger than {MIN_STAKING_SHARES_TO_MINT_OR_BURN}'
      )
    if self.share_amount > MAX_STAKING_SHARES_TO_MINT_OR_BURN:
      fail(
        f'StakeAssetsAmount should not be larger than {MAX_STAKING_SHARES_TO_MINT_OR_BURN}'
      )
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Pool, shares."""
    return [self.staking_pool_index, self.share_amount]

  def body_json(self) -> dict[str, Any]:
    """Pool, shares."""
    return {
      'StakingPoolIndex': self.staking_pool_index,
      'ShareAmount': self.share_amount,
    }


@dataclass(frozen=True, kw_only=True)
class UnstakeAssets(L2Tx):
  """`L2UnstakeAssets` (tx type 36): redeem shares of a staking pool.

  Go reports an out-of-range pool under the `PublicPoolIndex` messages here (whose text says
  -1 although the bound is the first sub-account index); reproduced as is.
  """

  staking_pool_index: int
  """Staking pool account (a sub-account index)."""
  share_amount: int
  """Shares to redeem."""

  TX_TYPE: ClassVar[int] = 36
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('staking_pool_index', 'StakingPoolIndex', 'int64'),
    ('share_amount', 'ShareAmount', 'int64'),
  )

  def check(self):
    """Go `L2UnstakeAssetsTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    if self.staking_pool_index < MIN_SUB_ACCOUNT_INDEX:
      fail(ERR_PUBLIC_POOL_INDEX_TOO_LOW)
    if self.staking_pool_index > MAX_ACCOUNT_INDEX:
      fail(ERR_PUBLIC_POOL_INDEX_TOO_HIGH)
    if self.share_amount < MIN_STAKING_SHARES_TO_MINT_OR_BURN:
      fail(
        f'UnstakeAssetsAmount should be larger than {MIN_STAKING_SHARES_TO_MINT_OR_BURN}'
      )
    if self.share_amount > MAX_STAKING_SHARES_TO_MINT_OR_BURN:
      fail(
        f'UnstakeAssetsAmount should not be larger than {MAX_STAKING_SHARES_TO_MINT_OR_BURN}'
      )
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Pool, shares."""
    return [self.staking_pool_index, self.share_amount]

  def body_json(self) -> dict[str, Any]:
    """Pool, shares."""
    return {
      'StakingPoolIndex': self.staking_pool_index,
      'ShareAmount': self.share_amount,
    }
