"""Coinbase App: the Consumer APIs tier — the only one this client implements today.
Business APIs (Coinbase Business) and Institutional APIs (Exchange, International Exchange,
Prime, Derivatives) are separate, unimplemented product families documented on the same
`docs.cdp.coinbase.com` host; this module scopes the client's actual surface honestly rather
than implying `Coinbase` covers all of them.
"""

from dataclasses import dataclass
import asyncio

from typed_coinbase.core.endpoint.rpc import RpcClient
from typed_coinbase.core.endpoint.stream import StreamClient
from .accounts import Accounts
from .advanced_trade import AdvancedTrade


@dataclass(kw_only=True)
class App:
  """Coinbase App (Consumer APIs).

  References:
    - [Coinbase App API docs](https://docs.cdp.coinbase.com/coinbase-app/docs/welcome)
  """

  accounts: Accounts
  """Coinbase App v2 — legacy accounts, transactions, transfers. Track (read) and Transfer
  (move) are documented as separate task categories upstream, but both are the same
  `/v2/accounts/...` REST surface, so they stay merged here.

  References:
    - [Track APIs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/accounts)
    - [Transfer APIs](https://docs.cdp.coinbase.com/coinbase-app/transfer-apis/send-crypto)
  """
  advanced_trade: AdvancedTrade
  """Advanced Trade (v3) — REST and both WebSocket connections.

  References:
    - [Advanced Trade overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/overview)
  """

  @classmethod
  def new(
    cls,
    *,
    http: RpcClient,
    market_data: StreamClient,
    user: StreamClient,
  ) -> 'App':
    """Build every product group from their own already-resolved transports.

    Args:
      http: Shared transport for both `accounts` and `advanced_trade.http`.
      market_data: Transport for the public WebSocket connection.
      user: Transport for the private WebSocket connection.
    """
    return cls(
      accounts=Accounts.new(client=http),
      advanced_trade=AdvancedTrade.new(http=http, market_data=market_data, user=user),
    )

  async def __aenter__(self) -> 'App':
    await asyncio.gather(self.accounts.__aenter__(), self.advanced_trade.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.accounts.__aexit__(exc_type, exc_value, traceback),
      self.advanced_trade.__aexit__(exc_type, exc_value, traceback),
    )
