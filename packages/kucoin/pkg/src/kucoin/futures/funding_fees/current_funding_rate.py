"""`GET /api/v1/funding-rate/{symbol}/current` — Get Current Funding Rate."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesCurrentFundingRate(TypedDict):
  """Current funding rate snapshot for one contract."""

  symbol: str
  """Funding rate symbol -- the underlying funding-rate index (e.g. `.XBTUSDTMFPI8H`), not the tradeable contract symbol passed in the request."""
  granularity: int
  """Funding interval, milliseconds. Confirmed live `28800000` (8 hours) for both probed contracts. A raw interval value, not a documented closed set of categories -- left bare rather than an enum."""
  timePoint: int
  """Settlement time point this record was generated for, Unix ms. Before a contract goes live KuCoin pre-generates the first record, so this is when the record was produced, not necessarily when it was (or will be) actually settled -- the first real settlement happens at the next 00:00/08:00/16:00 UTC boundary after listing."""
  value: float
  """Current cycle's funding rate."""
  dailyInterestRate: NotRequired[float]
  """Daily interest rate component used in the funding rate calculation. Undocumented by both the rendered docs page and the SDK's OpenAPI spec -- both instead document a `predictedValue` (next funding rate) field, which this endpoint did not return live for either contract probed (see notes)."""
  fundingRateCap: float
  """Maximum funding rate this contract permits."""
  fundingRateFloor: float
  """Minimum funding rate this contract permits."""
  period: Literal[1, 0]
  """Whether this record's funding is charged in the current cycle."""
  fundingTime: int
  """Next funding settlement time point, Unix ms -- usable to synchronize to the periodic settlement schedule."""


_Type = FuturesCurrentFundingRate
adapter = validator[_Type](_Type)  # type: ignore


class CurrentFundingRate(RpcEndpoint):
  """`Get Current Funding Rate` — mixed into `FundingFees`, the product exposing `futures.funding_fees.current_funding_rate`."""

  async def current_funding_rate(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> FuturesCurrentFundingRate:
    """Get the current cycle's funding rate for one futures contract, plus the predicted rate and cap/floor bounds used in its calculation.

    Args:
      symbol: Contract symbol, e.g. `XBTUSDTM`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      f'/api/v1/funding-rate/{symbol}/current',
      validator=adapter,
      validate=validate,
    )
