from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class Price(TypedDict):
  """A price quote in the requested currency pair."""

  amount: str
  """Price, as a decimal string."""
  currency: str
  """Quote currency of `amount`."""


class PriceResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core."""

  data: Price


@dataclass(frozen=True, kw_only=True)
class Buy(RpcEndpoint):
  """`GET /v2/prices/{currency_pair}/buy`."""

  async def buy(self, currency_pair: str) -> PriceResponse:
    """Get the total price, inclusive of fees, to buy one unit of the base currency. No authentication required.

    Args:
      currency_pair: Currency pair, e.g. `BTC-USD`.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/prices)
    """
    return await self.request(
      'GET', f'/v2/prices/{currency_pair}/buy', validator=validator(PriceResponse)
    )
