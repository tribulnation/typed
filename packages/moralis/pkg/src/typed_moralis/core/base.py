"""Moralis client root: shared transport and lifecycle.

One `MoralisTransport` (the raw HTTP client, the resolved API key, and the client-level
response-validation default) backs every product this client composes -- `evm`,
`bitcoin`, `universal`, `solana`, `auth`, `cortex`, `streams` all forward the identical
`self.client` unchanged. Unlike a single shared `RestEndpoint`, each product now resolves
to one of five host-scoped cores (`core/rest.py`'s `DeepIndexEndpoint`/`SolanaEndpoint`/
`AuthEndpoint`/`CortexEndpoint`/`StreamsEndpoint`), each baking its own fixed base URL
into `_base_url()` -- mirroring alchemy's `core.rest`/`core.rpc` pattern. The one wrinkle:
a distinct base host per top-level product is not quite that simple for every endpoint --
four endpoints physically living under `solana/`
(`solana/token/market_metrics/token_analytics{,_batch,_timeseries}`,
`solana/token_search`) are actually deep-index-hosted, not Solana-gateway-hosted like the
rest of `solana/`. `market_metrics/` resolves its own host independently of the rest of
`solana/`'s default. `token_search` needed a different placement entirely:
`solana/token/` already composes two other endpoints
(`token_metadata`/`token_metadata_batch`, both Solana-gateway-hosted) together through
Python inheritance, and mixing a differently-hosted endpoint into that same composed class
would let Python's own method-resolution order silently pick the wrong host for a shared
method -- multiple inheritance does not preserve which parent a given method's own
override "belongs to" once two parents both define it. `token_search` instead sits as
`solana/`'s own direct child, composed alongside no other bare endpoint at that position,
so there is nothing for its host to be silently overridden by.
"""

from dataclasses import dataclass, field
from typing_extensions import Self

from typed_core.http import HttpClient

from .auth import env_api_key


@dataclass(kw_only=True, frozen=True)
class MoralisTransport:
  """Shared low-level sender: the raw HTTP client, the resolved API key, and the
  client-level response-validation default -- every field a Moralis endpoint needs
  regardless of which product it belongs to.
  """

  http: HttpClient
  api_key: str = field(repr=False)
  validate: bool = True
  base_url: str | None = None
  """Override applied ahead of every core's own baked-in host (`core/rest.py`'s
  `_base_url()`) -- unset for real use (each core's own resolved host is always the right
  one), set to a single local mock-server address for testing (S19), since every
  product's endpoints replay against one mock server regardless of which real host each
  would otherwise call.
  """

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate


@dataclass(kw_only=True)
class ClientBase:
  """Root lifecycle: constructs and owns the shared transport every resolved core
  forwards unchanged. The generated root class (`main.Moralis`) subclasses this and this
  alone (design §4) -- never also a resolved core.
  """

  client: MoralisTransport

  @classmethod
  def new(
    cls, api_key: str | None = None, /, *,
    validate: bool = True,
    base_url: str | None = None,
    http: HttpClient | None = None,
  ) -> Self:
    """Create a Moralis client.

    Args:
      api_key: Moralis API key. Falls back to `MORALIS_API_KEY` when omitted.
      validate: Validate responses by default.
      base_url: Override applied ahead of every core's own baked-in host -- for
        pointing the whole client at a local mock server (S19), not for real use.
      http: Shared HTTP transport override.
    """
    key = env_api_key(api_key)
    return cls(
      client=MoralisTransport(
        http=http or HttpClient(), api_key=key, validate=validate, base_url=base_url,
      )
    )

  async def __aenter__(self) -> Self:
    """Open the underlying HTTP transport."""
    await self.client.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the underlying HTTP transport."""
    await self.client.http.__aexit__(exc_type, exc_value, traceback)
