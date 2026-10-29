# Swap Tokens

Gate DEX aggregates on-chain liquidity and is non-custodial: it quotes a swap and builds the
unsigned transaction, you sign it with your own wallet library, and Gate can broadcast it for
you. The client never holds wallet keys or signs transactions.

The flow is quote, approve (token inputs only), build, sign, submit, then track.

> **There is no testnet.** As of October 2026, Gate DEX runs on mainnet only: `trade.submit`
> broadcasts your signed transactions and spends real funds. Quoting and building move
> nothing; only what you submit or broadcast yourself does.

## Chains, DEXs And Tokens

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  chains = await client.trade.chains()  # chains swaps route on
  for chain in chains:
    print(chain['chain_id'], chain['chain_name'], chain['native_currency'])

  dexes = await client.trade.dexes(chain_id=1)  # DEXs and aggregators routed through
  tokens = await client.trade.tokens(chain_id='1', search='USDT')  # swappable tokens
  for token in tokens['tokens']:
    print(token['symbol'], token['address'], token['decimal'], token['current_price'])
```

Pass `wallet` to `tokens` to include that wallet's balances.

## Gas Prices

The shape depends on the chain family; check for a family's own key to narrow it:

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  gas = await client.trade.gas_price(chain_id=1)
  if 'base_wei_fee' in gas:  # EVM
    print(gas['base_wei_fee'], gas['avg_pri_wei_per_gas'], gas['support_eip1559'])
  elif 'avg_microlp_per_cu' in gas:  # Solana
    print(gas['avg_microlp_per_cu'])
```

Sui reports `*_mist_per_gas` and Tron `base_energy_price`/`base_bandwidth_price`. Gate has no
gas price for TON: `gas_price(chain_id=607)` raises `BadRequest` (code `20005`, `The current
chain is not supported`).

## The Whole Flow

Swapping 100 USDT for ETH on Ethereum:

```python
import json
from typed_gate_dex import GateDex
from typed_gate_dex.trade.build import UnsignedSwapTx

WALLET = '0xYourWalletAddress'
USDT = '0xdac17f958d2ee523a2206206994597c13d831ec7'


def sign_approval(token: str, data: str, gas_limit: int) -> str:
  """Sign a call to `token` carrying `data` with your wallet library (nonce N)."""
  raise NotImplementedError


def sign_swap(tx: UnsignedSwapTx) -> str:
  """Sign `tx` with your wallet library (nonce N + 1 after an approval)."""
  raise NotImplementedError


async with GateDex.new() as client:
  quote = await client.trade.quote(
    chain_id=1,
    amount_in='100',  # human-decimal: 100 USDT
    token_in=USDT,
    token_out='-',  # the chain's native coin
    slippage=0.01,  # 1%
    slippage_type=1,  # percentage
    user_wallet=WALLET,
  )
  print(quote['amount_out'], quote['min_amount_out'])

  approval = await client.trade.approve_transaction(
    user_wallet=WALLET, approve_amount='100', quote_id=quote['quote_id']
  )
  signed_approval = sign_approval(
    quote['from_token']['token_contract_address'], approval['data'], approval['gas_limit']
  )

  build = await client.trade.build(
    chain_id=1,
    amount_in='100',
    token_in=USDT,
    token_out='-',
    slippage=0.01,
    slippage_type=1,
    user_wallet=WALLET,
    receiver=WALLET,
    quote_id=quote['quote_id'],
  )
  signed_swap = sign_swap(build['unsigned_tx'])

  submitted = await client.trade.submit({  # broadcasts on mainnet
    'order_id': build['order_id'],
    'signed_tx_string': json.dumps([signed_swap]),
    'signed_approve_tx_string': json.dumps([signed_approval]),
  })

  order = await client.trade.status(
    chain_id=1, order_id=submitted['order_id'], tx_hash=submitted['tx_hash']
  )
  print(order['status'], order.get('amount_out'), order.get('error_msg'))
```

## Quote

Amounts are human-decimal (`'0.01'` ETH, not wei), as a string or `Decimal`. `'-'` stands for
the chain's native coin; the response reports it as its wrapped token (`WETH`, `WSOL`). With
`slippage_type=1`, `slippage` is a fraction (`0.01` is 1%); `slippage_type=2` takes a fixed
value. `fee_recipient` and `fee_rate` add your own fee, which Gate caps at 3%. As of October
2026, Gate does not settle the scale of `fee_rate`: its order records describe it as a
fraction (`0.03` is 3%), while the quote accepts values from `0.01` up to `5` without error.

## Approve

A token input (ERC-20 on EVM chains, TRC-20 on Tron) needs an allowance first;
`approve_transaction` returns the calldata. Send it to the input token's own contract, not to
`approval['approve_address']`, which is the spender encoded inside it. Native coins and other
chains need no approval.

## Build

`build` returns the unsigned transaction and opens an order, whose `order_id` can be
submitted once. Pass the `quote_id` so the build executes that quote. `unsigned_tx.value` is
in raw smallest units. Gate simulates the swap while building it and raises `ApiError`
(code `31500`, `execution reverted`) when the simulation fails.

## Sign

What `unsigned_tx` holds, and what Gate expects back, per chain family:

| Family | `unsigned_tx.data` | Signed form |
| --- | --- | --- |
| EVM | hex calldata, sent to `to` with `value` | EIP-1559 (type 2) transaction, `0x02...` hex |
| Solana | base64 `VersionedTransaction` | base58, after refreshing the recent blockhash |
| Sui | base64 `TransactionBlock` | base64 |
| TON | a message (`body`, `sendMode`) | base64 BOC |
| Tron | hex calldata, sent to the router `to` with `value` | not documented by Gate |

As of October 2026, Gate's API reference has signing samples for EVM, Solana, Sui and TON
only, and does not say what signed form it expects for Tron.

On EVM chains you supply the nonce, from your own node, and the fees, which `gas_price`
estimates. Sign the approval with nonce N and the swap with N + 1.

## Submit

Gate broadcasts what you submit, on mainnet. As of October 2026, Gate's sources disagree on
the format of `signed_tx_string` and `signed_approve_tx_string`. Its
[API reference](https://gateweb3.gitbook.io/gate_dex_api/trading-api/en/swap-api/publish-your-docs-4)
calls them strings without saying more, and its Go sample sends a bare `0x...` string. Gate's
[agent skills](https://github.com/gate/gate-skills) describe a JSON array encoded as a string
(`'["0x02f8..."]'`), which the example above follows with `json.dumps([...])`. They say a
bare hex string fails the order later, with `error_code` `50005`, and that legacy EVM
transactions are rejected; the Go sample signs EIP-1559 (type 2).

To broadcast yourself instead, submit the hash: `{'order_id': build['order_id'], 'tx_hash':
'0x...'}`.

## Track

`status` returns the order once it has been submitted; before that it raises `ApiError`
(`31701`, `Transaction not found`). Order amounts are raw smallest-unit integers (see
`token_out_decimals`). A failed swap is not an exception: its order carries `error_code` and
`error_msg`. Gate does not publish the values of `status`.

`history(user_wallet=[...])` lists a wallet's orders. As of October 2026, Gate answers every
history request with code `20009` (`JSON parse error`), raised as `BadRequest`; track orders
with `status` meanwhile.
