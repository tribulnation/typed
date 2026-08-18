"""`book.{instrument_name}.{interval}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class BookUpdate(TypedDict):
  """Real-time order book update. The first notification per subscription is a full `snapshot` (all price levels, no depth limit); subsequent notifications are `change` deltas against individual price levels."""

  instrument_name: str
  """Unique instrument identifier."""
  change_id: int
  """Identifier of the notification."""
  prev_change_id: NotRequired[int]
  """Identifier of the previous notification. Not present on the first (`snapshot`) notification."""
  timestamp: NotRequired[int]
  """The timestamp of the last change (milliseconds since the Unix epoch)."""
  type: NotRequired[Literal['snapshot', 'change']]
  """`snapshot` for the first notification, `change` for every later one."""
  bids: list[tuple[Literal['new', 'change', 'delete'], float, float]]
  """Bid-side level updates, all price levels on a `snapshot`."""
  asks: list[tuple[Literal['new', 'change', 'delete'], float, float]]
  """Ask-side level updates, all price levels on a `snapshot`."""


validate_book = validator[BookUpdate](BookUpdate)


class Book(StreamEndpoint):
  """`book.{instrument_name}.{interval}` subscription."""

  def book(
    self,
    instrument_name: str,
    interval: Literal['raw', '100ms', 'agg2'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[BookUpdate, Any, Any]:
    """Real-time order book updates for a specific instrument, with no depth limit. The first notification is a full snapshot of the book; subsequent notifications carry only incremental changes. Each notification carries a `change_id`, and every message but the first also carries `prev_change_id` -- if it equals the previous message's `change_id`, no messages were missed. For a depth-limited, price-grouped snapshot, use `book.{instrument_name}.{group}.{depth}.{interval}` instead.

    Args:
      instrument_name: The name of the instrument.
      interval: Frequency of notifications; events are aggregated over this interval. `raw` means no aggregation and is only available to authorized users.
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/orderbook/bookinstrument_nameinterval)
    """
    channel = f'book.{instrument_name}.{interval}'
    return self.subscribe(channel, validator=validate_book, validate=validate)
