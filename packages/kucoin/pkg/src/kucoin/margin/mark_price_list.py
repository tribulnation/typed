"""`GET /api/v3/mark-price/all-symbols` — Get Mark Price List."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class MarkPriceRow(TypedDict):
  symbol: str
  """Symbol."""
  timePoint: int
  """Timestamp this mark price was computed at, Unix milliseconds."""
  value: float
  """Mark price."""


_Type = list[MarkPriceRow]
adapter = validator[_Type](_Type)  # type: ignore


class MarkPriceList(RpcEndpoint):
  """`Get Mark Price List` — mixed into `Margin`, the product exposing `margin.mark_price_list`."""

  async def mark_price_list(
    self, *, validate: bool | None = None
  ) -> list[MarkPriceRow]:
    """Get the current mark price for every margin trading pair in one call.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      '/api/v3/mark-price/all-symbols',
      validator=adapter,
      validate=validate,
    )
