from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class FiatCurrency(TypedDict):
  """A fiat currency Coinbase recognizes."""

  id: str
  """Currency code, e.g. `USD`."""
  name: str
  """Currency display name."""
  min_size: str
  """Minimum representable unit for this currency, as a decimal string."""


class ListCurrenciesResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core."""

  data: list[FiatCurrency]
  """The known fiat currencies."""


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /v2/currencies`."""

  async def list(self) -> ListCurrenciesResponse:
    """List known fiat currencies. Currency codes conform to the ISO 4217 standard where possible. No authentication required.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/currencies)
    """
    return await self.request(
      'GET', '/v2/currencies', validator=validator(ListCurrenciesResponse)
    )
