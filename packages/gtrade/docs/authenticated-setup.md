# Wallet & Agent Setup

Public data needs no credentials: market data, the per-chain backend, Backend Global and
pricing all work with `GTrade.new(public=True)`. So do registering or revoking an agent and
issuing an API key, below: the master wallet's signature goes in the request instead.

Private Trading API calls take one of two credentials:

| Credential | Environment variable | Allows |
| - | - | - |
| Agent private key | `GTRADE_AGENT_PRIVATE_KEY` | Private reads, private channels, orders and positions |
| Read-only API key | `GTRADE_API_KEY` | Private reads and private channels |

The agent is a key registered for the trader. It signs every private request (EIP-712) and
the transactions the API prepares, and it pays their gas, so it needs a little ETH on the
chain. A read-only API key can never place an order.

Both are created with a one-off EIP-712 signature from the trader's master wallet:
`typed_gtrade.signing` builds the typed data, you sign it with whatever holds that key
(this page uses `eth_account`), and the signature goes in the request.

## Choose an Agent

| | Separate agent key | The trader's own wallet |
| - | - | - |
| On-chain setup | The master wallet sends one `setTradingDelegate` transaction (needs ETH for gas) | None |
| Key the client holds | The agent key; the master key stays out of the process | The master key |
| If that key leaks | It can trade with the trader's collateral, bound only by the chain (the API scope is not enforced on-chain), but cannot withdraw: PnL is always paid to the trader | It controls the wallet and every fund in it |
| Cutting it off | Revoke it, and the master wallet removes the on-chain delegation | Move the funds to a new wallet |

A separate agent is the setup to run unattended. Registering the trader's own wallet skips
the on-chain step, at the cost of giving the client the master key.

## Register a Separate Agent

```python
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from eth_account import Account
from typed_gtrade import GTrade
from typed_gtrade.signing import AgentScope, agent_authorization, sign_typed_data

master = Account.from_key('0x...')  # the trader's wallet, used only to sign
agent = Account.create()            # store agent.key.to_0x_hex() as GTRADE_AGENT_PRIVATE_KEY
now = datetime.now(timezone.utc)
scope: AgentScope = {
  'markets': ['BTC/USD', 'ETH/USD'],
  'maxLeverage': Decimal('10'),
  'dailySpendCapUsd': Decimal('1000'),
  'expiresAt': now + timedelta(days=30),
  'permissions': 'trade',
}

async with GTrade.new(public=True) as client:
  typed_data = agent_authorization(
    client.trading.signing_domain, agent=agent.address, name='my-bot', scope=scope, timestamp=now,
  )
  registration = await client.trading.agents.create(
    trader=master.address,
    agent=agent.address,
    name='my-bot',
    scope=scope,
    timestamp=now,
    signature=sign_typed_data(master, typed_data),
  )
  print(registration['agent']['status'])  # 'pending_delegation'
  delegation_tx = registration['delegationTx']  # {to, data, chainId}: send from the master wallet
```

Pass the same `name`, `scope` and `timestamp` to the builder and the request: the signature
covers exactly those values. `scope` limits the markets, the leverage, the daily notional
in USD, the expiry, and `trade` or `read`; any limit can be `None`. The API checks it
whenever it prepares a transaction. Without a client, take the domain from
`SigningDomain.for_chain('arbitrum')`, also in `typed_gtrade.signing`.

Registration, delegation and gas are all per chain: the agent is registered on the chain of
the client you register it with, and its signatures are bound to that chain. Repeat the
registration with a client built for each chain the agent trades on, then, on that chain:

1. Send `delegationTx` from the master wallet. The agent turns `active` when it is mined:
   check with `client.trading.agents.get(agent.address)`.
2. Send the agent a little ETH for gas.

### Use the Trader's Own Wallet

Pass `agent=master.address` to both calls. `delegationTx` is then `None` and there is
nothing to send, but `GTRADE_AGENT_PRIVATE_KEY` is the master key itself.

## Revoke an Agent

```python
from datetime import datetime, timezone
from eth_account import Account
from typed_gtrade import GTrade
from typed_gtrade.signing import agent_revocation, sign_typed_data

master = Account.from_key('0x...')
agent_address = '0x...'
now = datetime.now(timezone.utc)

async with GTrade.new(public=True) as client:
  typed_data = agent_revocation(client.trading.signing_domain, agent=agent_address, timestamp=now)
  revocation = await client.trading.agents.revoke(
    agent=agent_address, trader=master.address, timestamp=now, signature=sign_typed_data(master, typed_data),
  )
  removal_tx = revocation['revocationTx']  # send from the master wallet; None without a delegation
```

The API stops serving the agent at once. Until `revocationTx` is mined, the key remains the
trader's on-chain delegate.

## Issue a Read-Only API Key

```python
from datetime import datetime, timezone
from eth_account import Account
from typed_gtrade import GTrade
from typed_gtrade.signing import api_key_issue, sign_typed_data

master = Account.from_key('0x...')
now = datetime.now(timezone.utc)

async with GTrade.new(public=True) as client:
  typed_data = api_key_issue(client.trading.signing_domain, label='dashboard', timestamp=now)
  key = await client.trading.api_keys.issue(
    trader=master.address, label='dashboard', timestamp=now, signature=sign_typed_data(master, typed_data),
  )
  api_key = key['apiKey']  # shown once: store it as GTRADE_API_KEY
```

## Configure the Client

Put the credentials in a `.env` file and load it with `python-dotenv`
(`pip install python-dotenv`), or export the same variables in your shell instead:

```bash
# .env
GTRADE_AGENT_PRIVATE_KEY="0x..."
GTRADE_API_KEY="gk_..."
```

```python
from dotenv import load_dotenv
from typed_gtrade import GTrade

load_dotenv()

async with GTrade.new() as client:
  account = await client.trading.account.get('0x...')  # the trader address
```

Either variable is enough. With both, private reads and channels use the API key and writes
use the agent. Arguments replace the environment as a whole: `GTrade.new(agent='0x...')`
reads neither variable, so pass `api_key=` too to use both. `GTrade.new(public=True)` reads
neither and raises `ValueError` if given a credential.

Before the first order, the master wallet also approves the Diamond to spend its
collateral: see the [first trade checklist](how-to/place-and-manage-orders.md#first-trade-checklist).

See the upstream [authentication guide](https://docs.gains.trade/developer/trading-api/authentication)
for the full model.
