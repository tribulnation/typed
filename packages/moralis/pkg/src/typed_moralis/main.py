"""The Moralis client root."""

from dataclasses import dataclass
import asyncio

from typed_core.http import HttpClient as _HttpClient

from .auth import Auth
from .bitcoin import Bitcoin
from .core.auth import env_api_key
from .core.transport.http import (
  MORALIS_API_URL,
  MORALIS_AUTH_API_URL,
  MORALIS_CORTEX_API_URL,
  MORALIS_SOLANA_API_URL,
  MORALIS_STREAMS_API_URL,
  HttpRpcClient,
)
from .cortex import Cortex
from .evm import Evm
from .solana import Solana
from .streams import Streams
from .universal import Universal


@dataclass(kw_only=True)
class Moralis:
  """Moralis data-API client -- read-only EVM, Solana, Bitcoin, and cross-chain wallet/
  token/NFT data, an AI chat endpoint (`cortex`), wallet sign-in (`auth`), and webhook
  stream management (`streams`), all behind a single api-key-authenticated REST surface.

  Examples:
    ```python
    from typed_moralis import Moralis

    async with Moralis.new() as client:
      balances = await client.evm.wallet.token_balances('0x...', chain='eth')
      print(balances)
    ```
  """

  evm: Evm
  solana: Solana
  bitcoin: Bitcoin
  universal: Universal
  cortex: Cortex
  auth: Auth
  streams: Streams

  @classmethod
  def new(
    cls, api_key: str | None = None, /, *,
    base_url: str = MORALIS_API_URL,
    solana_base_url: str = MORALIS_SOLANA_API_URL,
    auth_base_url: str = MORALIS_AUTH_API_URL,
    cortex_base_url: str = MORALIS_CORTEX_API_URL,
    streams_base_url: str = MORALIS_STREAMS_API_URL,
    validate: bool = True,
    http: _HttpClient | None = None,
  ) -> 'Moralis':
    """Create a Moralis client.

    Args:
      api_key: Moralis API key. If omitted, falls back to `MORALIS_API_KEY`.
      base_url: Override for the EVM/Bitcoin/Universal ("deep-index") API base URL.
      solana_base_url: Override for the Solana data API base URL.
      auth_base_url: Override for the Auth API base URL.
      cortex_base_url: Override for the Cortex (AI chat) API base URL.
      streams_base_url: Override for the Streams webhook-management API base URL.
      validate: Validate responses by default.
      http: Shared HTTP transport override, reused across every product's client.
    """
    key = env_api_key(api_key)
    shared_http = http or _HttpClient()

    def client(url: str) -> HttpRpcClient:
      return HttpRpcClient(base_url=url, api_key=key, http=shared_http, validate=validate)

    deep_index = client(base_url)
    return cls(
      evm=Evm(client=deep_index),
      bitcoin=Bitcoin(client=deep_index),
      universal=Universal(client=deep_index),
      solana=Solana(client=client(solana_base_url)),
      auth=Auth(client=client(auth_base_url)),
      cortex=Cortex(client=client(cortex_base_url)),
      streams=Streams(client=client(streams_base_url)),
    )

  async def __aenter__(self) -> 'Moralis':
    """Open the underlying HTTP transport(s). `evm`, `bitcoin`, and `universal` share
    one transport instance (same host); entering it more than once is a documented
    no-op on `typed_core.http.HttpClient`.
    """
    await asyncio.gather(
      self.evm.__aenter__(),
      self.solana.__aenter__(),
      self.bitcoin.__aenter__(),
      self.universal.__aenter__(),
      self.cortex.__aenter__(),
      self.auth.__aenter__(),
      self.streams.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the underlying HTTP transport(s)."""
    await asyncio.gather(
      self.evm.__aexit__(exc_type, exc_value, traceback),
      self.solana.__aexit__(exc_type, exc_value, traceback),
      self.bitcoin.__aexit__(exc_type, exc_value, traceback),
      self.universal.__aexit__(exc_type, exc_value, traceback),
      self.cortex.__aexit__(exc_type, exc_value, traceback),
      self.auth.__aexit__(exc_type, exc_value, traceback),
      self.streams.__aexit__(exc_type, exc_value, traceback),
    )
