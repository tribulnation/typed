"""Alchemy client root: shared transport and lifecycle.

Every resolved `core` this client declares (`codegen/config.toml`'s `[python.cores]`, design
§5/§5a/§5c) -- REST or JSON-RPC, chain-scoped or not -- carries one `AlchemyTransport`
unchanged, the shared low-level sender every generated composite forwards as `self.client`
(`{Core}(client=self.client)`/`{Core}.new(self.client, ...)`, design §5a's own convention).
`ClientBase` builds it once and owns lifecycle (`.new()`, `__aenter__`/`__aexit__`); the
generated root class (`typed_alchemy.main.Alchemy`) subclasses `ClientBase` alone, never
also a resolved core (design §4) -- `Alchemy` itself declares no direct endpoints.
"""

from typing_extensions import Literal, Self, TypeAliasType
from dataclasses import dataclass

from typed_core.http import HttpClient

from .auth import resolve_api_key

Network = TypeAliasType(
  'Network',
  Literal[
    'ethereum',
    'bnb',
    'polygon',
    'base',
    'avalanche',
    'optimism',
    'arbitrum',
    'gnosis',
    'celo',
  ],
)
"""EVM chains this client wires a base URL for. Alchemy documents 100+ chains total
(`spec/discovery.md`'s Domains section); this is the pre-existing, already-wired subset,
carried over unchanged from the client's original hand-written core.

Declared via `TypeAliasType` rather than a plain assignment so the alias name survives
`typing_extensions.get_type_hints()` -- a plain `Network = Literal[...]` assignment is
erased by `get_type_hints()`, which hands back the raw expanded `Literal[...]` with no way
to recover the name `Network`, and every generated `main.py` factory method
(`nft`/`token`/`transfers`/`utility`/`simulation`) that takes a `network` parameter
introspects this alias through exactly that call (design §5a,
`typed_dev.codegen.python.Generator._new_param_type`)."""


@dataclass(kw_only=True, frozen=True)
class AlchemyTransport:
  """Shared low-level sender: the app API key, the client-level response-validation
  default, and construction-time base-URL overrides for the two fixed-host products --
  every field a resolved `core` might need regardless of which one it is.
  """

  http: HttpClient
  api_key: str
  validate: bool = True
  data_base_url: str | None = None
  """Fully-qualified Portfolio API base URL override, used as-is (bypassing the usual
  `api_key_url(portfolio_url(), api_key)` computation) when given -- mirrors the
  pre-migration `Alchemy.new(data_url=...)` parameter."""
  prices_base_url: str | None = None
  """Fully-qualified Prices API base URL override, used as-is when given -- mirrors the
  pre-migration `Alchemy.new(prices_url=...)` parameter."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate


@dataclass(kw_only=True)
class ClientBase:
  """Root lifecycle: constructs and owns the shared transport every resolved `core`
  forwards unchanged. The generated root class (`main.Alchemy`) subclasses this and this
  alone (design §4) -- never also a resolved `core`.
  """

  client: AlchemyTransport

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    validate: bool = True,
    data_url: str | None = None,
    prices_url: str | None = None,
    http: HttpClient | None = None,
  ) -> Self:
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
    return cls(
      client=AlchemyTransport(
        http=http or HttpClient(),
        api_key=key,
        validate=validate,
        data_base_url=data_url,
        prices_base_url=prices_url,
      )
    )

  async def __aenter__(self) -> Self:
    await self.client.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.http.__aexit__(exc_type, exc_value, traceback)
