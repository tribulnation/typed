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

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
