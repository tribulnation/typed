"""`GET /api/v1/contract/funding-rates` — Get Public Funding History."""

from typing_extensions import AsyncIterator
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesFundingRateSettlement(TypedDict):
  """One settled funding rate at one settlement time point."""

  symbol: str
  """Contract symbol."""
  fundingRate: float
  """Funding rate applied at this settlement."""
  timepoint: int
  """Settlement time point, Unix ms."""


_Type = list[FuturesFundingRateSettlement]
adapter = validator[_Type](_Type)  # type: ignore


class PublicFundingHistory(RpcEndpoint):
  """`Get Public Funding History` — mixed into `FundingFees`, the product exposing `futures.funding_fees.public_funding_history`."""

  async def public_funding_history(
    self,
    *,
    symbol: str,
    from_: int,
    to: int,
    validate: bool | None = None,
  ) -> list[FuturesFundingRateSettlement]:
    """Query one futures contract's settled funding rate at each settlement time point within a time window.

    Args:
      symbol: Contract symbol, e.g. `XBTUSDTM`.
      from_: Start of the window, Unix ms. Inclusive -- confirmed live (see notes). Genuinely required: an unfiltered call with `symbol` alone and no `from`/`to` was rejected (`400000 Bad Request`), contradicting the rendered docs page (which lists it optional) but matching the SDK's OpenAPI spec, which marks it `required: true`.
      to: End of the window, Unix ms. Inclusive -- confirmed live (see notes). Same required-in-practice finding as `from`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
      'from': from_,
      'to': to,
    }
    return await self.request(
      'GET',
      '/api/v1/contract/funding-rates',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def public_funding_history_paged(
    self,
    *,
    symbol: str,
    from_: int,
    to: int,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[FuturesFundingRateSettlement]]:
    """Yield successive pages of `public_funding_history`.

    Moves the `from_`–`to` window forwards by its own width and stops on the first empty
    window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `from_` and `to` state, so choose a
    window the venue answers in one response: it caps a wider one, and the walk moves
    past the rows that were left out.
    """
    lower = from_
    upper = to
    width = upper - lower
    pages = 0
    while True:
      response = await self.public_funding_history(
        symbol=symbol, from_=lower, to=upper, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      if not response:
        break
      lower = upper + 1
      upper = lower + width
