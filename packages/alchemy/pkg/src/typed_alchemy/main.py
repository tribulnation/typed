"""The Alchemy client root.

Composes the generated `api/**` tree (`typed-dev codegen python alchemy`, driven by
`codegen/python.py`) onto the new `core/endpoint` + `core/transport` architecture
`spec/core.md` documents. `portfolio`/`prices` are fields, since each has one fixed
host; `token`/`transfers`/`utility`/`simulation`/`nft` are methods, since each is
reachable over any of the 9 wired EVM chains and there is no canonical URL to bind
once at construction -- see `spec/core.md`'s Surfaces section for the full reasoning
(the same documented S11 deviation dYdX's `Indexer`/`Chain`/`Node` split is).
"""

from typed_core.http import HttpClient

from .core.auth import api_key_url, resolve_api_key
from .core.transport.http import (
  ApiKeyPathHttpClient,
  Network,
  chain_nft_url,
  chain_rpc_url,
  portfolio_url,
  prices_url as _default_prices_url,
)
from .api.nft import Nft
from .api.portfolio import Portfolio
from .api.portfolio.nft_contracts import NftContracts
from .api.portfolio.nfts import Nfts
from .api.portfolio.token_balances import TokenBalances
from .api.portfolio.tokens import Tokens
from .api.portfolio.transactions import Transactions
from .api.prices import Prices
from .api.simulation import Simulation
from .api.token import Token
from .api.transfers import Transfers
from .api.utility import Utility

from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Alchemy:
  """Alchemy client: Portfolio, Prices, and the per-chain JSON-RPC/NFT/Transfers/
  Utility/Simulation surfaces.

  `token`/`transfers`/`utility`/`simulation`/`nft` are methods, not fields,
  deliberately -- see the module docstring.

  Examples:
    ```python
    from typed_alchemy import Alchemy

    async with Alchemy.new() as client:
      result = await client.token('ethereum').get_token_balances('0x...')
    ```
  """

  portfolio: Portfolio
  prices: Prices
  _http: HttpClient
  _api_key: str = field(repr=False)
  _validate: bool

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    validate: bool = True,
    data_url: str | None = None,
    prices_url: str | None = None,
    http: HttpClient | None = None,
  ):
    """Create an Alchemy client.

    There is no `public=True` build: every surface this client implements requires the
    app API key as a literal path segment of the request URL itself, so there is no valid
    request to make without one -- see `spec/core.md`'s Authentication section.

    Args:
      api_key: Alchemy app API key. Falls back to `ALCHEMY_API_KEY` if omitted.
      validate: Validate responses by default.
      data_url: Fully-qualified Portfolio API base URL override, used as-is (bypassing
        the usual `api_key_url(...)` computation) when given.
      prices_url: Fully-qualified Prices API base URL override, used as-is when given.
      http: Shared HTTP client override, reused by every constructed surface.
    """
    key = resolve_api_key(api_key)
    shared_http = http or HttpClient()
    portfolio_client = ApiKeyPathHttpClient(
      base_url=data_url or api_key_url(portfolio_url(), key),
      http=shared_http,
      validate=validate,
    )
    return cls(
      portfolio=Portfolio(
        nft_contracts=NftContracts(client=portfolio_client),
        nfts=Nfts(client=portfolio_client),
        token_balances=TokenBalances(client=portfolio_client),
        tokens=Tokens(client=portfolio_client),
        transactions=Transactions(client=portfolio_client),
      ),
      prices=Prices(
        client=ApiKeyPathHttpClient(
          base_url=prices_url or api_key_url(_default_prices_url(), key),
          http=shared_http,
          validate=validate,
        )
      ),
      _http=shared_http,
      _api_key=key,
      _validate=validate,
    )

  def token(
    self, network: Network = 'ethereum', *, base_url: str | None = None
  ) -> Token:
    """Access the Token JSON-RPC API group for one chain.

    Args:
      network: EVM chain to query.
      base_url: Fully-qualified base URL override, used as-is when given.
    """
    return Token(
      client=ApiKeyPathHttpClient(
        base_url=base_url or api_key_url(chain_rpc_url(network), self._api_key),
        http=self._http,
        validate=self._validate,
      )
    )

  def transfers(
    self,
    network: Network = 'ethereum',
    *,
    base_url: str | None = None,
  ) -> Transfers:
    """Access the Transfers JSON-RPC API group for one chain.

    Args:
      network: EVM chain to query.
      base_url: Fully-qualified base URL override, used as-is when given.
    """
    return Transfers(
      client=ApiKeyPathHttpClient(
        base_url=base_url or api_key_url(chain_rpc_url(network), self._api_key),
        http=self._http,
        validate=self._validate,
      )
    )

  def utility(
    self,
    network: Network = 'ethereum',
    *,
    base_url: str | None = None,
  ) -> Utility:
    """Access the Utility JSON-RPC API group for one chain.

    Args:
      network: EVM chain to query.
      base_url: Fully-qualified base URL override, used as-is when given.
    """
    return Utility(
      client=ApiKeyPathHttpClient(
        base_url=base_url or api_key_url(chain_rpc_url(network), self._api_key),
        http=self._http,
        validate=self._validate,
      )
    )

  def simulation(
    self,
    network: Network = 'ethereum',
    *,
    base_url: str | None = None,
  ) -> Simulation:
    """Access the Simulation JSON-RPC API group for one chain.

    Args:
      network: EVM chain to query.
      base_url: Fully-qualified base URL override, used as-is when given.
    """
    return Simulation(
      client=ApiKeyPathHttpClient(
        base_url=base_url or api_key_url(chain_rpc_url(network), self._api_key),
        http=self._http,
        validate=self._validate,
      )
    )

  def nft(self, network: Network = 'ethereum', *, base_url: str | None = None) -> Nft:
    """Access the NFT API v3 group for one chain.

    Args:
      network: EVM chain to query.
      base_url: Fully-qualified base URL override, used as-is when given.
    """
    return Nft(
      client=ApiKeyPathHttpClient(
        base_url=base_url or api_key_url(chain_nft_url(network), self._api_key),
        http=self._http,
        validate=self._validate,
      )
    )

  async def __aenter__(self):
    await self._http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self._http.__aexit__(exc_type, exc_value, traceback)
