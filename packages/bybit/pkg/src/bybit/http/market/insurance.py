"""`GET /v5/market/insurance` — Get Insurance Pool."""

from typing_extensions import TypedDict
from bybit.core import Endpoint, validator


class InsurancePool(TypedDict):
  """One insurance pool."""

  coin: str
  """Coin held by the pool."""
  symbols: str
  """Comma-separated contracts backed by the pool; a single contract means the pool is isolated."""
  balance: str
  """Pool balance, in `coin`."""
  value: str
  """Pool balance valued in USD."""


class InsurancePools(TypedDict):
  """Insurance pool balances."""

  updatedTime: str
  """Time the balances were last updated, as a millisecond timestamp."""
  list: list[InsurancePool]
  """Insurance pools."""


adapter = validator[InsurancePools](InsurancePools)


class Insurance(Endpoint):
  """`Get Insurance Pool` — mixed into the router that owns `market.insurance`."""

  async def insurance(
    self,
    *,
    coin: str | None = None,
    validate: bool | None = None,
  ) -> InsurancePools:
    """Get the balance of each Bybit insurance pool and the contracts it backs.

    Args:
      coin: Settlement coin in uppercase. Defaults to every insurance coin.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/insurance)
    """
    params = {}
    if coin is not None:
      params['coin'] = coin
    r = await self.request('GET', '/v5/market/insurance', params=params)
    return self.result(r, adapter, validate)
