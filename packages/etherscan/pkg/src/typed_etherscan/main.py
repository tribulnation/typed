"""The Etherscan client root."""

from dataclasses import dataclass

from .core.auth import resolve_api_key, resolve_rate_limit
from .core.transport.http import HttpRpcClient, ETHERSCAN_API_URL
from .api.account import Account
from .api.blocks import Blocks
from .api.contracts import Contracts
from .api.gas_tracker import GasTracker
from .api.l2 import L2
from .api.logs import Logs
from .api.nametags import Nametags
from .api.proxy import Proxy
from .api.stats import Stats
from .api.tokens import Tokens
from .api.transactions import Transactions
from .api.usage import Usage


@dataclass(kw_only=True)
class Etherscan:
  """Etherscan API V2 client: one HTTP surface, multiplexed by `module`/`action` query
  parameters (plus `usage.chain_list`, the one endpoint outside that dispatch).

  Examples:
    ```python
    from typed_etherscan import Etherscan

    async with Etherscan.new() as client:
      balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
    ```
  """

  account: Account
  blocks: Blocks
  contracts: Contracts
  gas_tracker: GasTracker
  l2: L2
  logs: Logs
  nametags: Nametags
  proxy: Proxy
  stats: Stats
  tokens: Tokens
  transactions: Transactions
  usage: Usage

  @classmethod
  def new(
    cls, api_key: str | None = None, *,
    rate_limit: int | None = None, public: bool = False,
    base_url: str = ETHERSCAN_API_URL, validate: bool = True,
  ):
    """Build an Etherscan client.

    Args:
      api_key: Etherscan API key; read from `ETHERSCAN_API_KEY` when omitted.
      rate_limit: Client-side calls-per-second cap; read from `ETHERSCAN_RATE_LIMIT` when
        omitted.
      public: Skip credential resolution -- only `usage.chain_list` is reachable then.
      base_url: Etherscan API host.
      validate: Validate responses by default.
    """
    client = HttpRpcClient(
      base_url=base_url,
      api_key=resolve_api_key(api_key, public=public),
      rate_limit=resolve_rate_limit(rate_limit),
      validate=validate,
    )
    return cls(
      account=Account(client=client),
      blocks=Blocks(client=client),
      contracts=Contracts(client=client),
      gas_tracker=GasTracker(client=client),
      l2=L2(client=client),
      logs=Logs(client=client),
      nametags=Nametags(client=client),
      proxy=Proxy(client=client),
      stats=Stats(client=client),
      tokens=Tokens(client=client),
      transactions=Transactions(client=client),
      usage=Usage(client=client),
    )

  async def __aenter__(self):
    """Every section shares one transport client, so opening any one of them opens it."""
    await self.account.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.account.__aexit__(exc_type, exc_value, traceback)
