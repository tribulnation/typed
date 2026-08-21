# Environment Variables

```bash
ETHERSCAN_API_KEY="your_api_key"
ETHERSCAN_RATE_LIMIT="4"
```

- `ETHERSCAN_API_KEY` — required for every method except `usage.chain_list`. Read by
  `Etherscan.new()` when `api_key` isn't passed directly. See
  [API keys setup](../api-keys.md).
- `ETHERSCAN_RATE_LIMIT` — optional client-side cap on calls per second. Read by
  `Etherscan.new()` when `rate_limit` isn't passed directly; unset means no client-side cap,
  only Etherscan's own reactive one.

Both are only ever read from the environment, never from any other source, and only inside
`Etherscan.new()`.
