# RPC Provider Credentials

`NodeRpc.public_node(network)` uses a public RPC endpoint and requires no key,
private key, funded wallet, or exchange account.

For Alchemy, call `NodeRpc.alchemy(network, api_key=...)` with a provider key
loaded by your application. If `api_key` is omitted, that constructor reads
`ALCHEMY_API_KEY` from the environment. It does not load a `.env` file itself.

For another HTTP provider, use `NodeRpc.at(rpc_url)`. Provider authentication may
be embedded in the URL; do not log or commit secret-bearing URLs.

There are no `ETHEREUM_API_KEY` or `ETHEREUM_API_SECRET` variables in this client.
See [Environment Variables](reference/env-vars.md).
