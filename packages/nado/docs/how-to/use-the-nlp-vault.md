# Use The NLP Vault

NLP is Nado's liquidity-provider vault: you mint NLP with USDT0 and burn it back later.
Freshly minted NLP is locked for a period before it can be burned. Pool state and history
are public; minting and burning are signed executes.

## Pool State And History

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  info = await client.gateway.nlp_pool_info()
  for pool in info['nlp_pools']:
    print(pool['pool_id'], pool['balance_weight_x18'] / 10**18)

  snapshots = await client.archive.nlp_snapshots(limit=24)
  for snapshot in snapshots['snapshots']:
    print(snapshot['timestamp'], snapshot['tvl'] / 10**18, snapshot['cumulative_pnl'] / 10**18)
```

Funding and interest paid to the vault are in `archive.nlp_funding_payments` and
`archive.nlp_interest_payments`.

## Your Position

```python
from typed_nado import Nado

async with Nado.new() as client:
  balances = await client.gateway.nlp_locked_balances()
  print(balances['balance_locked']['balance']['amount'] / 10**18)
  print(balances['balance_unlocked']['balance']['amount'] / 10**18)
  for locked in balances['locked_balances']:
    print(locked['balance']['balance']['amount'] / 10**18, 'unlocks at', locked['unlocked_at'])

  mintable = await client.gateway.max_nlp_mintable()
  burnable = await client.gateway.max_nlp_burnable()
  print(mintable['max_quote_amount'] / 10**18, burnable['max_nlp_amount'] / 10**18)
```

## Mint And Burn

Both amounts are x18: `quoteAmount` is the USDT0 to spend, `nlpAmount` the NLP to burn.

> **Real funds:** this signs and executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

```python
from typed_nado import Nado

async with Nado.new() as client:
  await client.gateway.mint_nlp({'quoteAmount': 100 * 10**18})
  await client.gateway.burn_nlp({'nlpAmount': 50 * 10**18})
```

Only unlocked NLP can be burned: check `max_nlp_burnable` first.
