# Async Usage

dYdX clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine.

```python
from typed_dydx import Dydx

client = Dydx.testnet(public=True)
market = await client.indexer.data.get_market('BTC-USD')
print(market)
```

The indexer's HTTP and WebSocket transports open lazily on first use, the same as every
other Typed client.

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block.

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  market = await client.indexer.data.get_market('BTC-USD')
  block = await client.chain.comet.block()
```

`Dydx.__aenter__` enters `client.indexer` and `client.chain` together -- you never
separately enter a sub-client. This is the recommended style for multiple requests,
long-lived sessions, any streaming workflow, or code where explicit cleanup matters.

## The Chain gRPC Exception

Every other transport in this catalog opens lazily: entering it via `async with` does not,
by itself, open a live connection -- only the first actual request does. dYdX's `chain`
surface is the one confirmed exception.

`Chain.__aenter__` enters both the gRPC `modules` client and the Comet HTTP client, and
`GrpcClient.__aenter__` explicitly forces construction of the underlying
`grpclib.client.Channel` immediately on entry:

```
# GrpcClient.__aenter__ (chain/core.py)
async def __aenter__(self) -> Self:
  """Open the channel for an async client context."""
  self.channel
  return self
```

So `async with Dydx.mainnet(public=True) as client:` (or `async with Chain.mainnet() as
chain:` on its own) opens the gRPC channel right away, not on the first `client.chain.*`
call. This only matters when you use `async with` -- plain construction without a context
manager still opens the channel lazily, on first use, the same as everything else.

## Streams

`client.indexer.streams` groups every indexer WebSocket subscription --
`block_height`, `candles`, `markets`, `orders`, `parent_subaccounts`, `subaccounts`,
`trades` -- built on `typed_core.ws.streams.Streams`. Each call returns a `StreamManager`.

Use `async with` on the manager so the subscription is unsubscribed automatically when the
block exits:

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  async with client.indexer.streams.candles('ETH-USD', resolution='1MIN') as candles:
    async for candle in candles:
      print(candle)
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  candles = await client.indexer.streams.candles('ETH-USD', resolution='1MIN')
  async for candle in candles:
    print(candle)
    break
  await candles.unsubscribe()
```

## Composite/Multi-Surface Client

`Dydx` composes three surfaces:

- `indexer` -- HTTP + WebSocket, market data, account history, and streams
- `chain` -- gRPC + Comet HTTP, shared read-only chain state, entered eagerly on the gRPC
  side (see above)
- `node` -- a wallet/signing wrapper around `chain` for order placement and transactions.
  `node.public` is a plain lazy `@property` returning `Public(self.chain)`, not a separate
  transport -- it just proxies read-only queries onto the already-open `chain`

`Dydx.new(...)` builds this from raw options. Every named provider constructor --
`.oegs()`, `.mainnet()`, `.polkachu()`, `.kingnodes()`, `.enigma()`, plus their `_archive`
and `testnet_*` counterparts -- funnels through `.new()` with a different `Chain` provider
preset.

## Guidance

Use direct construction for quick reads.

Use `async with` by default when:

- you are doing more than one call
- you are opening streams
- you want predictable cleanup -- for `chain`, this also means the gRPC channel opens
  immediately rather than on first use
