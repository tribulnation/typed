# Environment Variables

`NodeRpc.public_node(network)` and `NodeRpc.at(rpc_url)` read no client-defined
credential environment variables.

`NodeRpc.alchemy(network)` reads `ALCHEMY_API_KEY` only when its `api_key` argument
is omitted. If neither is supplied, construction raises `KeyError`. Passing the
argument explicitly avoids that environment lookup.

The client does not load `.env` files. Provider keys belong in your application's
secret configuration, not source code. No Ethereum private key or exchange API
secret is required for the balance helpers.
