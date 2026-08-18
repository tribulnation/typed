from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class ExchangeRates(TypedDict):
  """Exchange rates for one unit of the base currency, against every other currency Coinbase tracks."""

  currency: str
  """The base currency these rates are quoted against."""
  rates: dict[str, str]
  """Map of currency code to the exchange rate for one unit of `currency`, as a decimal string."""


class ExchangeRatesResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core."""

  data: ExchangeRates


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /v2/exchange-rates`."""

  async def list(self, *, currency: str | None = None) -> ExchangeRatesResponse:
    """Get current exchange rates for a base currency against every other currency Coinbase tracks. No authentication required.

    Args:
      currency: Base currency for the returned rates. Defaults to `USD`.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/exchange-rates)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    return await self.request(
      'GET',
      '/v2/exchange-rates',
      params=params,
      validator=validator(ExchangeRatesResponse),
    )
