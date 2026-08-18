"""`/contract/instrument:{symbol}` — Subscribe to mark price, index price and funding rate pushes for one futures contract. Mark/index price pushes roughly once a second; the (predicted) funding rate pushes roughly once a minute -- two different push shapes share this one topic, told apart structurally (only a mark/index push carries `markPrice`/`indexPrice`; only a funding-rate push carries `fundingRate`), since the wire frame's discriminating `subject` field never reaches the caller (`SocketStreamClient.subscribe` strips the envelope down to `data`; see `spec/core.md`'s WebSocket section)."""

from typing_extensions import Any, Literal
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class FuturesFundingRateEvent(TypedDict):
  """Predicted funding rate update, pushed roughly once a minute (wire `subject: "funding.rate"`) -- not the settled funding rate itself, which is pushed on the Contract Announcement channel (`streams.futures.announcement`)."""

  fundingRate: float
  """Current predicted funding rate."""
  granularity: int
  """Push interval, in milliseconds. The venue's machine spec's prose ('predicted funding rate: 1-min granularity: 60000; Funding rate: 8-hours granularity: 28800000') is internally ambiguous about whether this branch's value is `60000` or `28800000` -- left bare rather than a guessed `enum` (spec-authoring rule 2); see `notes`."""
  timestamp: int
  """Unix milliseconds when this push was generated."""


class FuturesMarkIndexPriceEvent(TypedDict):
  """Mark/index price snapshot, pushed roughly once a second (wire `subject: "mark.index.price"`)."""

  markPrice: float
  """Current mark price."""
  indexPrice: float
  """Current index price."""
  granularity: Literal[1000]
  """Push interval, in milliseconds."""
  timestamp: int
  """Unix milliseconds when this push was generated."""


_Type = FuturesMarkIndexPriceEvent | FuturesFundingRateEvent
validate_update = validator[_Type](_Type)  # type: ignore


class Instrument(StreamEndpoint):
  """Subscribe to `/contract/instrument:{symbol}` — mixed into `Market`, the product exposing `streams.futures.instrument`."""

  def instrument(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[FuturesMarkIndexPriceEvent | FuturesFundingRateEvent, Any, Any]:
    """Subscribe to mark price, index price and funding rate pushes for one futures contract. Mark/index price pushes roughly once a second; the (predicted) funding rate pushes roughly once a minute -- two different push shapes share this one topic, told apart structurally (only a mark/index push carries `markPrice`/`indexPrice`; only a funding-rate push carries `fundingRate`), since the wire frame's discriminating `subject` field never reaches the caller (`SocketStreamClient.subscribe` strips the envelope down to `data`; see `spec/core.md`'s WebSocket section).

    Args:
      symbol: Contract symbol to watch, for example `XBTUSDTM`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/contract/instrument:{symbol}',
      validator=validate_update,
      validate=validate,
    )
