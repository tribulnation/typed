# Authenticated Setup

Margin Trade has no API keys. Every signed request carries an Ed25519 signature from a
Solana-style keypair, and your account *is* that key's public address.

Market data, account reads by address, and streams need no key at all:

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  mids = await client.info.all_mids()
```

## Master Key

Trading, transfers, withdrawals, the signed `user` calls and every `solana` call need a
wallet. Put the private key in your environment and pass it to `MarginTrade.new`; the client
never reads the environment on its own. A client is either public or signed: passing a
wallet (or `vault`) together with `public=True` raises `ValueError`.

```python
import os
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  print(client.account)  # your account address
  profile = await client.user.get_user()
```

The key can be any format `Wallet.parse` accepts:

1. a hex 32-byte seed (64 hex digits, `0x` optional), the API docs' format;
2. a base58 64-byte Solana secret key (seed followed by public key), as the web app's
   API-wallet page shows it; its public half must match the seed;
3. a base58 32-byte seed;
4. raw `bytes`: a 32-byte seed, or a 64-byte seed followed by its public key.

Anything else raises `AuthError`. Call `Wallet.parse` yourself if you want the address
before building a client, and `Wallet.generate()` creates a fresh account: a new
key works immediately, with no web-app onboarding.

`mainnet=False` selects testnet (`testnet-api.margin.trade`) and signs every request for it.
Leave it out for mainnet.

## Agent Key (API Wallet)

An agent is a second key the master approves to trade on its behalf. Sign with the agent and
pass the master address as `vault`:

```python
import os
from typed_margin_trade import MarginTrade, Wallet

master = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])

async with MarginTrade.new(
  os.environ['MARGIN_TRADE_TESTNET_AGENT_PRIVATE_KEY'], vault=master.address, mainnet=False
) as client:
  orders = await client.info.open_orders(user=master.address)
```

Approve an agent from the master with `client.exchange.approve_agent(agent_address=...)`
and list approvals with `client.exchange.get_agents()`.

`approve_agent_v2` additionally carries the agent's own consent, so the approval proves you
hold the agent key. Sign it with `agent_consent`, passing the client's network: the network
code is part of the signed consent, so it is only valid there.

```python
import os
from typed_margin_trade import MarginTrade, Wallet, agent_consent

master = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])
agent = Wallet.generate()

async with MarginTrade.new(master, mainnet=False) as client:
  consent = agent_consent(agent, master=master.address, network=client.network)
  await client.exchange.approve_agent_v2(
    agent_address=agent.address,
    agent_consent_signature=consent['signature'],
    agent_consent_timestamp=consent['timestamp'],
  )
```

Agent management (`approve_agent`, `approve_agent_v2`, `revoke_agent`, `get_agents`) and
`exchange.withdraw` are master-only: an agent client refuses them with `AuthError` before
anything is sent.

## Testnet Funds

On testnet, claim test USDC once per UTC day:

```python
import os
from typed_margin_trade import MarginTrade

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  claim = await client.user.faucet_claim()
  print(claim['amount'], claim['nextClaimAt'])
```

`faucet_claim` is testnet-only; on mainnet it raises `BadRequest` without sending.
