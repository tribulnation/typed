"""Account transactions: change API key (8), create sub-account (9), update leverage (20),
update margin (29), account config (41), account asset config (42) and approve integrator (45).

Ported from lighter-go v1.0.10 `types/txtypes/{change_pub_key,create_sub_account,
update_leverage,update_margin,update_account_config,update_account_asset_config,
approve_integrator}.go`, validation order and messages included.
"""

from typing_extensions import Any, ClassVar
from dataclasses import dataclass

from .base import (
  ERR_ACCOUNT_INDEX_TOO_HIGH,
  ERR_ACCOUNT_INDEX_TOO_LOW,
  ERR_FROM_ACCOUNT_INDEX_TOO_HIGH,
  ERR_FROM_ACCOUNT_INDEX_TOO_LOW,
  ERR_INVALID_MARKET_INDEX,
  FEE_TICK,
  MARGIN_FRACTION_TICK,
  MAX_ACCOUNT_INDEX,
  MAX_MARKET_INDEX,
  MAX_MASTER_ACCOUNT_INDEX,
  MAX_TIMESTAMP,
  MAX_TRANSFER_AMOUNT,
  NIL_MARKET_INDEX,
  GoType,
  L2Tx,
  b64,
  check_account,
  check_api_key,
  check_asset,
  check_nonce_and_expiry,
  fail,
  go_json,
  hex10,
)

CROSS_MARGIN, ISOLATED_MARGIN = 0, 1
"""Position margin modes."""
REMOVE_FROM_ISOLATED_MARGIN, ADD_TO_ISOLATED_MARGIN = 0, 1
"""Isolated margin update directions."""

ERR_INVALID_MARGIN_MODE = 'MarginMode is not valid'

TEMPLATE_CHANGE_PUB_KEY = (
  'Register Lighter Account\n\npubkey: 0x{}\nnonce: {}\naccount index: {}\n'
  'api key index: {}\nOnly sign this message for a trusted client!'
)
"""Go `TemplateChangePubKey`."""
TEMPLATE_APPROVE_INTEGRATOR = (
  'Approve Integrator\n\nnonce: {}\naccount index: {}\napi key index: {}\n'
  'integrator account index: {}\nmax perps taker fee: {}\nmax perps maker fee: {}\n'
  'max spot taker fee: {}\nmax spot maker fee: {}\napproval expiry: {}\nchainId: {}\n'
  'Only sign this message for a trusted client!'
)
"""Go `TemplateL2ApproveIntegrator`."""


def check_from_account(value: int, *, maximum: int = MAX_ACCOUNT_INDEX):
  """The signing account, reported under Go's `FromAccountIndex` messages."""
  check_account(
    value,
    low=ERR_FROM_ACCOUNT_INDEX_TOO_LOW,
    high=ERR_FROM_ACCOUNT_INDEX_TOO_HIGH,
    maximum=maximum,
  )


@dataclass(frozen=True, kw_only=True)
class ChangePubKey(L2Tx):
  """`L2ChangePubKey` (tx type 8): register `pub_key` in the `api_key_index` slot.

  Signed on L2 by the key being registered, and on L1 by the account's Ethereum wallet
  (`l1_message`). The L1 signature does not enter the L2 hash.
  """

  pub_key: bytes
  """The 40-byte public key to register."""

  TX_TYPE: ClassVar[int] = 8

  def check_types(self):
    """Go integer type checks; `PubKey` must be bytes (Go's own rule checks its length)."""
    super().check_types()
    if not isinstance(self.pub_key, bytes):
      fail('PubKey is invalid')

  def check(self):
    """Go `L2ChangePubKeyTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)
    if len(self.pub_key) != 40:
      fail('PubKey is invalid')

  def body_elements(self) -> list[int]:
    """The public key's five raw little-endian limbs."""
    return [int.from_bytes(self.pub_key[i : i + 8], 'little') for i in range(0, 40, 8)]

  def body_json(self) -> dict[str, Any]:
    """Unused: `tx_info` places `L1Sig` between `PubKey` and `ExpiredAt`."""
    return {}

  def tx_info(self, sig: bytes, *, l1_sig: str = '') -> str:
    """Go's JSON: `PubKey` as base64, then `L1Sig`."""
    return go_json(
      {
        'AccountIndex': self.account_index,
        'ApiKeyIndex': self.api_key_index,
        'PubKey': b64(self.pub_key),
        'L1Sig': l1_sig,
        'ExpiredAt': self.expired_at,
        'Nonce': self.nonce,
        'Sig': b64(sig),
        'L2TxAttributes': self.attributes.to_json(),
      }
    )

  def l1_message(self, chain_id: int) -> str:
    """Go `GetL1SignatureBody` (no chain id in this one)."""
    return TEMPLATE_CHANGE_PUB_KEY.format(
      self.pub_key.hex(),
      hex10(self.nonce),
      hex10(self.account_index),
      hex10(self.api_key_index),
    )


@dataclass(frozen=True, kw_only=True)
class CreateSubAccount(L2Tx):
  """`L2CreateSubAccount` (tx type 9), signed by a master account."""

  TX_TYPE: ClassVar[int] = 9

  def check(self):
    """Go `L2CreateSubAccountTxInfo.Validate`: the signer must be a master account."""
    check_from_account(self.account_index, maximum=MAX_MASTER_ACCOUNT_INDEX)
    check_api_key(self.api_key_index)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """No fields of its own."""
    return []

  def body_json(self) -> dict[str, Any]:
    """No fields of its own."""
    return {}


@dataclass(frozen=True, kw_only=True)
class UpdateLeverage(L2Tx):
  """`L2UpdateLeverage` (tx type 20): a market's margin mode and initial margin fraction."""

  market_index: int
  """Market id."""
  initial_margin_fraction: int
  """Initial margin fraction in 1e-4 units (10_000 / leverage), in [1, 10_000]."""
  margin_mode: int
  """`CROSS_MARGIN` or `ISOLATED_MARGIN`."""

  TX_TYPE: ClassVar[int] = 20
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('market_index', 'MarketIndex', 'int16'),
    ('initial_margin_fraction', 'InitialMarginFraction', 'uint16'),
    ('margin_mode', 'MarginMode', 'uint8'),
  )

  def check(self):
    """Go `L2UpdateLeverageTxInfo.Validate` (which only rejects the nil market 255)."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    if self.market_index == NIL_MARKET_INDEX:
      fail(ERR_INVALID_MARKET_INDEX)
    if self.margin_mode not in (CROSS_MARGIN, ISOLATED_MARGIN):
      fail(ERR_INVALID_MARGIN_MODE)
    if self.initial_margin_fraction <= 0:
      fail('InitialMarginFraction should not be less than 0')
    if self.initial_margin_fraction > MARGIN_FRACTION_TICK:
      fail(f'InitialMarginFraction should not be larger than {MARGIN_FRACTION_TICK}')
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Market, initial margin fraction, margin mode."""
    return [self.market_index, self.initial_margin_fraction, self.margin_mode]

  def body_json(self) -> dict[str, Any]:
    """Market, initial margin fraction, margin mode."""
    return {
      'MarketIndex': self.market_index,
      'InitialMarginFraction': self.initial_margin_fraction,
      'MarginMode': self.margin_mode,
    }


@dataclass(frozen=True, kw_only=True)
class UpdateMargin(L2Tx):
  """`L2UpdateMargin` (tx type 29): move USDC into or out of an isolated position.

  The amount is split for hashing with an *arithmetic* shift of the signed `int64`
  (`USDCAmount >> 32`), unlike the `uint64` splits of transfers and withdrawals; Go's
  validation lets a negative amount through, and both are reproduced.
  """

  market_index: int
  """Market id of the isolated position."""
  usdc_amount: int
  """USDC amount in 1e-6 units."""
  direction: int
  """`REMOVE_FROM_ISOLATED_MARGIN` or `ADD_TO_ISOLATED_MARGIN`."""

  TX_TYPE: ClassVar[int] = 29
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('market_index', 'MarketIndex', 'int16'),
    ('usdc_amount', 'USDCAmount', 'int64'),
    ('direction', 'Direction', 'uint8'),
  )

  def check(self):
    """Go `L2UpdateMarginTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    if (
      self.market_index < 0
      or self.market_index == NIL_MARKET_INDEX
      or self.market_index > MAX_MARKET_INDEX
    ):
      fail(ERR_INVALID_MARKET_INDEX)
    if self.usdc_amount == 0:
      fail('TransferAmount should be larger than 1')
    if self.usdc_amount > MAX_TRANSFER_AMOUNT:
      fail(f'TransferAmount should not be larger than {MAX_TRANSFER_AMOUNT}')
    if self.direction not in (REMOVE_FROM_ISOLATED_MARGIN, ADD_TO_ISOLATED_MARGIN):
      fail('Margin movement direction is not valid')
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Market, the amount's low and (arithmetically shifted) high 32 bits, direction."""
    return [
      self.market_index,
      self.usdc_amount & 0xFFFFFFFF,
      self.usdc_amount >> 32,
      self.direction,
    ]

  def body_json(self) -> dict[str, Any]:
    """Market, amount, direction."""
    return {
      'MarketIndex': self.market_index,
      'USDCAmount': self.usdc_amount,
      'Direction': self.direction,
    }


@dataclass(frozen=True, kw_only=True)
class UpdateAccountConfig(L2Tx):
  """`L2UpdateAccountConfig` (tx type 41): the account's trading mode."""

  account_trading_mode: int
  """0 or 1 (the unified trading account switch)."""

  TX_TYPE: ClassVar[int] = 41
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('account_trading_mode', 'AccountTradingMode', 'uint8'),
  )

  def check(self):
    """Go `L2UpdateAccountConfigTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    if self.account_trading_mode not in (0, 1):
      fail('AccountTradingMode is invalid')
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Trading mode."""
    return [self.account_trading_mode]

  def body_json(self) -> dict[str, Any]:
    """Trading mode."""
    return {'AccountTradingMode': self.account_trading_mode}


@dataclass(frozen=True, kw_only=True)
class UpdateAccountAssetConfig(L2Tx):
  """`L2UpdateAccountAssetConfig` (tx type 42): use an asset as margin, or not."""

  asset_index: int
  """Asset id in [1, 62]."""
  asset_margin_mode: int
  """0 disabled, 1 enabled."""

  TX_TYPE: ClassVar[int] = 42
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('asset_index', 'AssetIndex', 'int16'),
    ('asset_margin_mode', 'AssetMarginMode', 'uint8'),
  )

  def check(self):
    """Go `L2UpdateAccountAssetConfigTxInfo.Validate`."""
    check_from_account(self.account_index)
    check_api_key(self.api_key_index)
    check_asset(self.asset_index)
    if self.asset_margin_mode not in (0, 1):
      fail(ERR_INVALID_MARGIN_MODE)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Asset, margin mode."""
    return [self.asset_index, self.asset_margin_mode]

  def body_json(self) -> dict[str, Any]:
    """Asset, margin mode."""
    return {'AssetIndex': self.asset_index, 'AssetMarginMode': self.asset_margin_mode}


@dataclass(frozen=True, kw_only=True)
class ApproveIntegrator(L2Tx):
  """`L2ApproveIntegrator` (tx type 45): cap the fees an integrator may charge, until an expiry.

  All-zero fees with a zero expiry revoke an approval. Carries an L1 signature
  (`l1_message`) unless the integrator shares the master account or all fees are zero.
  """

  integrator_account_index: int
  """Integrator account."""
  max_perps_taker_fee: int
  """Fee cap in 1e-6 units, at most 1_000_000."""
  max_perps_maker_fee: int
  """Fee cap in 1e-6 units, at most 1_000_000."""
  max_spot_taker_fee: int
  """Fee cap in 1e-6 units, at most 1_000_000."""
  max_spot_maker_fee: int
  """Fee cap in 1e-6 units, at most 1_000_000."""
  approval_expiry: int
  """Epoch milliseconds the approval ends, or 0 to revoke."""

  TX_TYPE: ClassVar[int] = 45
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('integrator_account_index', 'IntegratorAccountIndex', 'int64'),
    ('max_perps_taker_fee', 'MaxPerpsTakerFee', 'uint32'),
    ('max_perps_maker_fee', 'MaxPerpsMakerFee', 'uint32'),
    ('max_spot_taker_fee', 'MaxSpotTakerFee', 'uint32'),
    ('max_spot_maker_fee', 'MaxSpotMakerFee', 'uint32'),
    ('approval_expiry', 'ApprovalExpiry', 'int64'),
  )

  def fees(self) -> list[int]:
    """The four fee caps, in declaration order."""
    return [
      self.max_perps_taker_fee,
      self.max_perps_maker_fee,
      self.max_spot_taker_fee,
      self.max_spot_maker_fee,
    ]

  def check(self):
    """Go `L2ApproveIntegratorTxInfo.Validate`."""
    check_account(
      self.account_index, low=ERR_ACCOUNT_INDEX_TOO_LOW, high=ERR_ACCOUNT_INDEX_TOO_HIGH
    )
    check_api_key(self.api_key_index)
    check_account(
      self.integrator_account_index,
      low='IntegratorAccountIndex should not be less than -1',
      high=f'IntegratorAccountIndex should not be larger than {MAX_ACCOUNT_INDEX}',
    )
    if any(fee > FEE_TICK for fee in self.fees()):
      fail(f'MarketFee should not be larger than {FEE_TICK}')
    if self.approval_expiry == 0 and any(self.fees()):
      fail('ApprovalExpiry should be zero when revoking integrator approval')
    if self.approval_expiry < 0 or self.approval_expiry > MAX_TIMESTAMP:
      fail('ApprovalExpiry is invalid')
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Integrator, fee caps, approval expiry."""
    return [self.integrator_account_index, *self.fees(), self.approval_expiry]

  def body_json(self) -> dict[str, Any]:
    """Integrator, fee caps, approval expiry."""
    return {
      'IntegratorAccountIndex': self.integrator_account_index,
      'MaxPerpsTakerFee': self.max_perps_taker_fee,
      'MaxPerpsMakerFee': self.max_perps_maker_fee,
      'MaxSpotTakerFee': self.max_spot_taker_fee,
      'MaxSpotMakerFee': self.max_spot_maker_fee,
      'ApprovalExpiry': self.approval_expiry,
    }

  def tx_info(self, sig: bytes, *, l1_sig: str = '') -> str:
    """Go's JSON, with `L1Sig` after `Sig`."""
    return go_json(
      {
        'AccountIndex': self.account_index,
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
    """Go `GetL1SignatureBody(chainId)`."""
    return TEMPLATE_APPROVE_INTEGRATOR.format(
      hex10(self.nonce),
      hex10(self.account_index),
      hex10(self.api_key_index),
      hex10(self.integrator_account_index),
      *(hex10(fee) for fee in self.fees()),
      hex10(self.approval_expiry),
      hex10(chain_id),
    )
