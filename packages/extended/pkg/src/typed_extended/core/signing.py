"""Completing a signed request body: filling the defaults signing depends on, fetching the
venue parameters it needs, and attaching the Stark `settlement` objects.

The caller's request carries the trade itself (market, side, size, price, ...). The core
fills, when absent: `nonce` (random in `[1, 2^31]`), `expiryEpochMillis` (now + 1 hour, as
the vendor SDK does), `fee` (the account's maker rate for post-only orders, taker rate
otherwise, from `GET /user/fees`) and `id` (the order's message hash, as the vendor SDK
does). It reads the market's `l2Config` (`GET /info/markets`), the receiving sub-account
(`GET /user/accounts`), the account's bridge address (`GET /user/account/info`) and
asset ids and resolutions (`GET /info/assets`) through a `SigningContext`, which caches
them for the life of the client.
"""

from typing_extensions import Any, Literal, NotRequired, Protocol, TypedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from .exc import BadRequest
from .networks import NetworkProfile
from .stark.settlement import (
  TRANSFER_EXPIRATION,
  WITHDRAWAL_EXPIRATION,
  L2Config,
  Side,
  StarkAccount,
  entire_position_size,
  expiration_from_now,
  new_nonce,
  sign_order,
  sign_transfer,
  sign_withdrawal,
)

DEFAULT_ORDER_LIFETIME = timedelta(hours=1)
"""How long an order without `expiryEpochMillis` lives (the vendor SDK's default)."""


@dataclass(frozen=True, kw_only=True)
class MarketSettlement:
  """What signing needs to know about one market."""

  l2: L2Config
  """Stark asset ids and resolutions."""
  min_order_size_change: Decimal
  """Size increment, which fixes an entire-position TP/SL leg's precision."""
  max_position_value: Decimal
  """Largest position value, which bounds an entire-position TP/SL leg's size."""


@dataclass(frozen=True, kw_only=True)
class FeeRates:
  """The account's fee rates on one market (`GET /user/fees`)."""

  maker: Decimal
  """Maker fee rate, for post-only orders."""
  taker: Decimal
  """Taker fee rate, for every other order."""


@dataclass(frozen=True, kw_only=True)
class SubAccount:
  """A sub-account's Stark identity (`GET /user/accounts`, `GET /user/account/info`)."""

  account_id: int
  """Account id."""
  l2_key: int
  """Stark public key."""
  l2_vault: int
  """Vault (position id)."""
  bridge_starknet_address: int | None
  """Starknet address EVM withdrawals are sent to."""


@dataclass(frozen=True, kw_only=True)
class AssetSettlement:
  """An asset's Stark id and resolution (`GET /info/assets`)."""

  stark_id: int
  """The asset's `starkexId`."""
  resolution: int
  """Quantums per unit (`starkexResolution`)."""


class SigningContext(Protocol):
  """Venue parameters signing needs, fetched (and cached) by the REST transport."""

  async def market_settlement(self, market: str) -> MarketSettlement:
    """A market's settlement parameters."""
    ...

  async def fee_rates(self, market: str) -> FeeRates:
    """The account's fee rates on a market."""
    ...

  async def sub_accounts(self) -> list[SubAccount]:
    """Every sub-account of the wallet."""
    ...

  async def account_info(self) -> SubAccount:
    """The sub-account the API key belongs to."""
    ...

  async def asset_settlement(self, asset: str) -> AssetSettlement:
    """An asset's Stark id and resolution, by name."""
    ...


class TpslLeg(TypedDict):
  """A take-profit or stop-loss leg as sent, before its settlement is attached."""

  price: str
  settlement: NotRequired[Any]
  debuggingAmounts: NotRequired[Any]


def opposite(side: Side) -> Side:
  """The other side."""
  return 'SELL' if side == 'BUY' else 'BUY'


def now_millis(now: datetime | None = None) -> int:
  """The current time, in epoch milliseconds."""
  return int((now or datetime.now(timezone.utc)).timestamp() * 1000)


async def prepare_order(
  body: dict[str, Any],
  *,
  account: StarkAccount,
  network: NetworkProfile,
  context: SigningContext,
  now: datetime | None = None,
) -> dict[str, Any]:
  """Complete and sign an order body (`POST /user/order`, `/user/order/rfq`).

  The order itself is signed at its own side, size and price; for a `TPSL` order (whose
  own `settlement` is omitted) each leg is signed at the order's side, and for any other
  order each attached leg is signed at the opposite side. A `POSITION`-sized leg is signed
  for the largest size the market allows, so the position can never outgrow it.

  Raises:
    BadRequest: The body is missing the market, side or size.
  """
  try:
    market_name: str = body['market']
    side: Side = body['side']
    qty = Decimal(body['qty'])
  except KeyError as e:
    raise BadRequest(f'An order needs {e.args[0]!r}') from None
  price = Decimal(body.get('price') or '0')
  market = await context.market_settlement(market_name)
  if body.get('fee') is None:
    rates = await context.fee_rates(market_name)
    body['fee'] = str(rates.maker if body.get('postOnly') else rates.taker)
  fee_rate = Decimal(body['fee']) + Decimal(body.get('builderFee') or '0')
  nonce = int(body['nonce']) if body.get('nonce') is not None else new_nonce()
  body['nonce'] = str(nonce)
  if body.get('expiryEpochMillis') is None:
    body['expiryEpochMillis'] = now_millis(now) + int(
      DEFAULT_ORDER_LIFETIME.total_seconds() * 1000
    )
  expiry = int(body['expiryEpochMillis'])

  def sign(leg_side: Side, leg_qty: Decimal, leg_price: Decimal):
    """Sign one order or leg with the shared parameters."""
    return sign_order(
      account=account,
      domain=network.domain,
      l2=market.l2,
      side=leg_side,
      qty=leg_qty,
      price=leg_price,
      fee_rate=fee_rate,
      nonce=nonce,
      expiry_millis=expiry,
    )

  signed = sign(side, qty, price)
  is_tpsl = body.get('type') == 'TPSL'
  if not is_tpsl:
    body['settlement'] = signed.settlement
  body['debuggingAmounts'] = signed.debugging_amounts
  if body.get('id') is None:
    body['id'] = str(signed.msg_hash)
  tp_sl_type: Literal['ORDER', 'POSITION'] | None = body.get('tpSlType')
  for key in ('takeProfit', 'stopLoss'):
    leg: TpslLeg | None = body.get(key)
    if leg is None:
      continue
    leg_price = Decimal(leg['price'])
    leg_qty = (
      entire_position_size(
        price=leg_price,
        min_order_size_change=market.min_order_size_change,
        max_position_value=market.max_position_value,
      )
      if tp_sl_type == 'POSITION'
      else qty
    )
    leg_signed = sign(side if is_tpsl else opposite(side), leg_qty, leg_price)
    leg['settlement'] = leg_signed.settlement
    leg['debuggingAmounts'] = leg_signed.debugging_amounts
  return body


async def prepare_transfer(
  body: dict[str, Any],
  *,
  account: StarkAccount,
  network: NetworkProfile,
  context: SigningContext,
  now: datetime | None = None,
) -> dict[str, Any]:
  """Sign a transfer body (`POST /user/transfer`: `fromAccount`, `toAccount`, `amount`,
  `transferredAsset`), resolving the receiving sub-account's vault and key.

  Raises:
    BadRequest: The body is incomplete, or `toAccount` is not a sub-account of the wallet.
  """
  try:
    to_account = int(body['toAccount'])
    amount = Decimal(body['amount'])
    asset_name: str = body['transferredAsset']
  except KeyError as e:
    raise BadRequest(f'A transfer needs {e.args[0]!r}') from None
  receiver = next(
    (a for a in await context.sub_accounts() if a.account_id == to_account), None
  )
  if receiver is None:
    raise BadRequest(f'Account {to_account} is not a sub-account of this wallet')
  asset = await context.asset_settlement(asset_name)
  body['settlement'] = sign_transfer(
    account=account,
    domain=network.domain,
    receiver_vault=receiver.l2_vault,
    receiver_public_key=receiver.l2_key,
    asset_id=asset.stark_id,
    resolution=asset.resolution,
    amount=amount,
    nonce=new_nonce(),
    expiration=expiration_from_now(TRANSFER_EXPIRATION, now),
  )
  return body


async def prepare_withdrawal(
  body: dict[str, Any],
  *,
  account: StarkAccount,
  network: NetworkProfile,
  context: SigningContext,
  now: datetime | None = None,
) -> dict[str, Any]:
  """Sign a withdrawal body (`POST /user/withdrawal`: `amount`, `asset`, `chainId`, ...).

  The recipient is the body's own `recipient` (a Starknet address, removed before
  sending), or for an EVM chain the account's `bridgeStarknetAddress`. `accountId` defaults
  to the API key's account.

  Raises:
    BadRequest: The body is incomplete, or no recipient can be determined (a Starknet
      withdrawal needs an explicit `recipient`).
  """
  try:
    amount = Decimal(body['amount'])
    asset_name: str = body['asset']
    chain: str = body['chainId']
  except KeyError as e:
    raise BadRequest(f'A withdrawal needs {e.args[0]!r}') from None
  recipient_value = body.pop('recipient', None)
  info: SubAccount | None = None
  if recipient_value is None or body.get('accountId') is None:
    info = await context.account_info()
    body.setdefault('accountId', info.account_id)
  if recipient_value is not None:
    recipient = (
      int(recipient_value, 16)
      if isinstance(recipient_value, str)
      else int(recipient_value)
    )
  elif (
    chain != 'STRK' and info is not None and info.bridge_starknet_address is not None
  ):
    recipient = info.bridge_starknet_address
  else:
    raise BadRequest(
      'A Starknet (STRK) withdrawal needs an explicit `recipient` address'
    )
  asset = await context.asset_settlement(asset_name)
  body['settlement'] = sign_withdrawal(
    account=account,
    domain=network.domain,
    recipient=recipient,
    asset_id=asset.stark_id,
    resolution=asset.resolution,
    amount=amount,
    nonce=new_nonce(),
    expiration=expiration_from_now(WITHDRAWAL_EXPIRATION, now),
  )
  return body


PREPARERS = {
  'order': prepare_order,
  'transfer': prepare_transfer,
  'withdrawal': prepare_withdrawal,
}
"""The body completer for each signed call kind."""
