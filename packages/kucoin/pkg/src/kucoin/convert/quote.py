"""`GET /api/v1/convert/quote` — Get Convert Quote."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class ConvertQuote(TypedDict):
  """A market convert quote, locking a price for a short window."""

  quoteId: str
  """Quote id; pass to Add Convert Order to execute a conversion at this price."""
  price: str
  """Quoted exchange rate, `toCurrency` per `fromCurrency`."""
  fromCurrencySize: str
  """Amount of `fromCurrency` this quote covers."""
  toCurrencySize: str
  """Amount of `toCurrency` this quote covers."""
  validUntill: int
  """Unix milliseconds this quote expires. Sic: the venue's own field name misspells `validUntil`."""


_Type = ConvertQuote
adapter = validator[_Type](_Type)  # type: ignore


class Quote(RpcEndpoint):
  """`Get Convert Quote` — mixed into `Convert`, the product exposing `convert.quote`."""

  async def quote(
    self,
    *,
    from_currency: str,
    to_currency: str,
    from_currency_size: str | None = None,
    to_currency_size: str | None = None,
    validate: bool | None = None,
  ) -> ConvertQuote:
    """Get a market convert quote for a currency pair, locking a price for a short window. Pass `quoteId` to `convert.add_order` to execute the conversion at this price.

    Args:
      from_currency: Source currency, for example `USDT`.
      to_currency: Target currency, for example `BTC`.
      from_currency_size: Amount of `fromCurrency` to convert. Exactly one of `fromCurrencySize`/`toCurrencySize` is required by the venue -- it prices the conversion from whichever side an amount was given for.
      to_currency_size: Desired amount of `toCurrency`. Exactly one of `fromCurrencySize`/`toCurrencySize` is required by the venue.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'fromCurrency': from_currency,
      'toCurrency': to_currency,
    }
    if from_currency_size is not None:
      params['fromCurrencySize'] = from_currency_size
    if to_currency_size is not None:
      params['toCurrencySize'] = to_currency_size
    return await self.authed_request(
      'GET',
      '/api/v1/convert/quote',
      params=params,
      validator=adapter,
      validate=validate,
    )
