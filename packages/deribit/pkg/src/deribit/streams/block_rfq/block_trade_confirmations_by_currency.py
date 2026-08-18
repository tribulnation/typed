"""`block_trade_confirmations.{currency}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class BlockTradeConfirmationLeg(TypedDict):
  instrument_name: str
  """Unique instrument identifier."""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`."""
  price: float
  """Price in base currency."""
  amount: float
  """Trade amount. For perpetual and inverse futures the amount is in USD units. For options and linear futures it is the underlying base currency coin."""


class BlockTradeConfirmation(TypedDict):
  """A pending block trade requiring this account's approval (or an update on one already handled)."""

  nonce: str
  """Nonce that can be used to approve or reject the pending block trade."""
  timestamp: int
  """Timestamp that can be used to approve or reject the pending block trade."""
  trades: list[BlockTradeConfirmationLeg]
  """Legs of the proposed block trade."""
  app_name: str
  """The name of the application that executed the block trade on behalf of the user (optional)."""
  username: NotRequired[str]
  """Username of the user who initiated the block trade."""
  role: Literal['maker', 'taker']
  """Trade role of the user."""
  user_id: int
  """Unique user identifier."""
  broker_code: NotRequired[str]
  """Broker code associated with the broker block trade."""
  broker_name: NotRequired[str]
  """Name of the broker associated with the block trade."""
  state: dict[str, Any]
  """State of the pending block trade for the current user. The venue documents no closed shape beyond an example carrying `value`/`timestamp`."""
  counterparty_state: NotRequired[dict[str, Any]]
  """State of the pending block trade for the other party (optional)."""
  combo_id: NotRequired[str]
  """Combo instrument identifier."""


validate_block_trade_confirmations_by_currency = validator[BlockTradeConfirmation](
  BlockTradeConfirmation
)


class BlockTradeConfirmationsByCurrency(StreamEndpoint):
  """`block_trade_confirmations.{currency}` subscription."""

  def block_trade_confirmations_by_currency(
    self,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[BlockTradeConfirmation, Any, Any]:
    """Notifications about pending block trades awaiting this account's approval, filtered to one currency (or all currencies, with `any`).

    Use this channel to react when a counterparty proposes a block trade that needs approving or rejecting (see `private/approve_block_trade` / `private/reject_block_trade`).

    Args:
      currency: Currency code or `any` for all

    **Allowed values:** `BTC`, `ETH`, `USDC`, `USDT`, `EURR`, `any`
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/block-trade/block_trade_confirmationscurrency)
    """
    channel = f'block_trade_confirmations.{currency}'
    return self.authed_subscribe(
      channel,
      validator=validate_block_trade_confirmations_by_currency,
      validate=validate,
    )
