# Use a Hosted RPC Provider

Authentication here means access to a node provider, not exchange trading or a
wallet-signing identity. Public balance reads do not require wallet credentials.

Configure an Alchemy key outside source code, then use `NodeRpc.alchemy(network)`.
It reads `ALCHEMY_API_KEY` unless an explicit `api_key` is supplied. For other HTTP
providers, construct `NodeRpc.at(rpc_url)` using your application's configured URL.

Use either client inside `async with`. See [RPC Provider Credentials](../api-keys.md)
for configuration and secret-handling boundaries.
