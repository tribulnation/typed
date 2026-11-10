"""The EIP-712 typed data a trader's master wallet signs to register or revoke an agent and
to issue a read-only API key.

The master key never reaches the client: build the typed data here, sign it with whatever
holds that key, and pass the signature, with the same values, to
`trading.agents.create`, `trading.agents.revoke` or `trading.api_keys.issue`. Each builder
takes exactly the values its endpoint takes (`Decimal` limits, `datetime` times) and
encodes them as the request body does, so the signature always covers the values sent.

Examples:
  Register a fresh agent key: the master wallet signs, and only the agent key is ever
  given to a trading client (`GTrade.new(agent=agent)`, once the master wallet has sent
  the `setTradingDelegate` transaction `agents.create` returns).

  ```python
  from datetime import datetime, timezone
  from eth_account import Account
  from typed_gtrade import GTrade
  from typed_gtrade.signing import AgentScope, agent_authorization, sign_typed_data

  master = Account.from_key('0x...')  # signs here, never passed to a client
  agent = Account.create()  # the key the trading client will hold
  scope: AgentScope = {
    'markets': 'all',
    'maxLeverage': None,
    'dailySpendCapUsd': None,
    'expiresAt': None,
    'permissions': 'trade',
  }
  now = datetime.now(timezone.utc)

  async with GTrade.new(public=True) as client:
    data = agent_authorization(
      client.trading.signing_domain,
      agent=agent.address,
      name='bot',
      scope=scope,
      timestamp=now,
    )
    await client.trading.agents.create(
      trader=master.address,
      agent=agent.address,
      name='bot',
      scope=scope,
      timestamp=now,
      signature=sign_typed_data(master, data),
    )
  ```
"""

from .core.auth import (
  AgentScope,
  SigningDomain,
  agent_authorization,
  agent_revocation,
  api_key_issue,
  sign_typed_data,
)

__all__ = [
  'AgentScope',
  'SigningDomain',
  'agent_authorization',
  'agent_revocation',
  'api_key_issue',
  'sign_typed_data',
]
