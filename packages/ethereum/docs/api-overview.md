# API Overview

The public root is `NodeRpc`, a small wrapper around Web3.py, not a generated
exchange endpoint tree.

## Construction and ownership

1. `NodeRpc.at(rpc_url, poa_middleware=False)` creates an HTTP provider.
2. `NodeRpc.public_node(network)` selects a bundled public HTTP URL.
3. `NodeRpc.alchemy(network, api_key=None)` selects an Alchemy HTTP URL.
4. `NodeRpc(w3=...)` accepts a caller-constructed `AsyncWeb3[AsyncBaseProvider]`.

Use `async with client`. Persistent providers are entered and exited through
Web3.py; HTTP providers are disconnected on exit. Do not independently close a
provider while a client using it is active.

## Balance helpers

1. `await client.eth_balance(address)` returns a native-asset `Decimal` amount.
2. `await client.token_balance(address, token_address=...)` returns an ERC-20
   `Decimal` amount using the token's reported decimals. Supply checksum addresses.
3. `client.token(token_address)` creates an ERC-20 helper and normalizes the token
   address to checksum form. Its async methods are `symbol()`, `decimals()`,
   `raw_balance(address)` and `balance(address)`; `decode_input(input)` is synchronous.
4. `client.w3` exposes the underlying Web3.py client for other node operations.

## Networks

Bundled URL maps cover `ethereum`, `bnb-chain`, `polygon`, `base`, `optimism`,
`avalanche`, `arbitrum` and `hyperevm`. Endpoint availability and service limits
belong to the chosen provider; a bundled URL is not an availability guarantee.

## Boundaries

There are no exchange tickers, order APIs, portfolio-history discovery, automatic
paging helpers, `.streams` namespace, or client-wide `validate=False` option.
RPC/ABI decoding and transport behavior come from Web3.py. Errors are not translated
into typed-core exception classes. See [Error Handling](reference/error-handling.md).
