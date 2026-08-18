"""`GET /api/v1/prices` — Get Fiat Price."""

from typed_core.validation import validator
from kucoin.core import RpcEndpoint


_Type = dict[str, str]
adapter = validator[_Type](_Type)  # type: ignore


class FiatPrice(RpcEndpoint):
  """`Get Fiat Price` — mixed into `Spot`, the product exposing `spot.fiat_price`."""

  async def fiat_price(
    self,
    *,
    base: str | None = None,
    currencies: str | None = None,
    validate: bool | None = None,
  ) -> dict[str, str]:
    """Get the fiat price of tradable currencies. Defaults to USD if `base` is omitted, and to every currency if `currencies` is omitted.

    Args:
      base: Fiat currency to price against, e.g. `USD`, `EUR`. Defaults to `USD`.
      currencies: Comma-separated crypto currencies to price, e.g. `BTC,ETH`. Defaults to all currencies.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if base is not None:
      params['base'] = base
    if currencies is not None:
      params['currencies'] = currencies
    return await self.request(
      'GET',
      '/api/v1/prices',
      params=params,
      validator=adapter,
      validate=validate,
    )
