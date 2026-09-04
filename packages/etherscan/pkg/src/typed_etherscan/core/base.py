"""Etherscan client root: shared transport and lifecycle.

Every resolved `core` this client declares (`codegen/config.toml`'s `[python.cores]`, design
§5) shares one `EtherscanTransport` unchanged -- the shared low-level sender the
generated composite forwards as `self.client` (`{Core}(client=self.client)`, design
§5a's own convention for a core with no `.new()` of its own). Etherscan has exactly one
resolved leaf core (`core.rest:RpcEndpoint`) -- design §5's degenerate single-core case,
the same shape most of the fleet is in. `ClientBase` builds the transport once and owns
lifecycle (`.new()`, `__aenter__`/`__aexit__`); the generated root class
(`typed_etherscan.main.Etherscan`) subclasses `ClientBase` alone, never also a resolved
core (design §4) -- `Etherscan` itself declares no direct endpoints.
"""

from typing_extensions import Self
from dataclasses import dataclass

from typed_core.http import HttpClient
from typed_core.util import RateLimit

from .auth import resolve_api_key, resolve_rate_limit

ETHERSCAN_API_URL = 'https://api.etherscan.io'
"""Host shared by both of Etherscan's V2 paths: `/v2/api` (module/action dispatch) and
`/v2/chainlist` (the one endpoint outside that dispatch)."""


@dataclass(kw_only=True, frozen=True)
class EtherscanTransport:
  """Shared low-level sender: the base URL, the resolved API key, the client-side rate
  limit, and the client-level response-validation default -- every field a resolved
  `core` might need."""

  http: HttpClient
  base_url: str = ETHERSCAN_API_URL
  api_key: str | None = None
  """`None` means credential-free: only an endpoint declaring `meta: {}`
  (`usage.chain_list`) is reachable then."""
  rate_limit: RateLimit | None = None
  """Client-side calls-per-second cap, cooperative rather than reactive -- Etherscan's
  free tier enforces a strict one."""
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate


@dataclass(kw_only=True)
class ClientBase:
  """Root lifecycle: constructs and owns the shared transport every resolved `core`
  forwards unchanged. The generated root class (`main.Etherscan`) subclasses this and
  this alone (design §4) -- never also a resolved `core`.
  """

  client: EtherscanTransport

  @classmethod
  def new(
    cls, api_key: str | None = None, *,
    rate_limit: int | None = None, public: bool = False,
    base_url: str = ETHERSCAN_API_URL, validate: bool = True,
    http: HttpClient | None = None,
  ) -> Self:
    """Build an Etherscan client.

    Args:
      api_key: Etherscan API key; read from `ETHERSCAN_API_KEY` when omitted.
      rate_limit: Client-side calls-per-second cap; read from `ETHERSCAN_RATE_LIMIT` when
        omitted.
      public: Skip credential resolution -- only `usage.chain_list` is reachable then.
      base_url: Etherscan API host.
      validate: Validate responses by default.
      http: Shared HTTP client override, reused by every constructed surface.
    """
    return cls(
      client=EtherscanTransport(
        http=http or HttpClient(),
        base_url=base_url,
        api_key=resolve_api_key(api_key, public=public),
        rate_limit=resolve_rate_limit(rate_limit),
        validate=validate,
      )
    )

  async def __aenter__(self) -> Self:
    await self.client.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.http.__aexit__(exc_type, exc_value, traceback)
