"""`instrument.state.{kind}.{currency}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class InstrumentStateUpdate(TypedDict):
  """Instrument lifecycle notification (new listing, expiration, termination)."""

  timestamp: NotRequired[int]
  """The timestamp (milliseconds since the Unix epoch)."""
  state: NotRequired[
    Literal[
      'open', 'settlement', 'delivered', 'inactive', 'locked', 'halted', 'archivized'
    ]
  ]
  """The state of the order book, i.e. the instrument's current lifecycle stage: `open` (live trading), `settlement` (settlement/delivery in progress), `delivered` (delivered, final), `inactive` (deactivated), `locked` (only cancels accepted), `halted` (error state), `archivized` (moved to expired instruments, final)."""
  instrument_name: NotRequired[str]
  """Unique instrument identifier."""


validate_instrument_state = validator[InstrumentStateUpdate](InstrumentStateUpdate)


class InstrumentState(StreamEndpoint):
  """`instrument.state.{kind}.{currency}` subscription."""

  def instrument_state(
    self,
    kind: Literal['future', 'option', 'spot', 'future_combo', 'option_combo'],
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[InstrumentStateUpdate, Any, Any]:
    """Notifications about new or terminated instruments of a given kind in a given currency -- lifecycle events (new listings, expirations/terminations) without polling. The venue does not send notifications when a currency is locked; subscribe to `platform_state` to monitor that.

    Args:
      kind: Instrument kind.
      currency: Currency code, or `any` for all.
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/market-data/instrumentstatekindcurrency)
    """
    channel = f'instrument.state.{kind}.{currency}'
    return self.subscribe(
      channel, validator=validate_instrument_state, validate=validate
    )
