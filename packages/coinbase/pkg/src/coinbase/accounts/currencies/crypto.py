from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class CryptoCurrency(TypedDict):
  """A cryptocurrency Coinbase recognizes."""

  code: str
  """Currency code, e.g. `BTC`."""
  name: str
  """Currency display name."""
  color: str
  """Brand color, as a hex string."""
  sort_index: int
  """Coinbase's display sort order for this currency."""
  exponent: int
  """Number of decimal places the currency's smallest unit represents."""
  type: str
  """Currency kind. Observed example value `crypto`; not documented as an exhaustive enumeration."""
  address_regex: str
  """Regex an onchain deposit address for this currency must match."""
  asset_id: str
  """Coinbase's internal asset id."""


class ListCryptoCurrenciesResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core. Verified live: this endpoint is wrapped in `data` the same as every sibling v2 endpoint, contrary to an earlier assumption that it returned a bare array."""

  data: list[CryptoCurrency]
  """The known cryptocurrencies."""


@dataclass(frozen=True, kw_only=True)
class Crypto(RpcEndpoint):
  """`GET /v2/currencies/crypto`."""

  async def crypto(self) -> ListCryptoCurrenciesResponse:
    """List known cryptocurrencies. No authentication required.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/currencies)
    """
    return await self.request(
      'GET', '/v2/currencies/crypto', validator=validator(ListCryptoCurrenciesResponse)
    )
