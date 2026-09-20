# Environment Variables

| Variable | Required for | Description |
|---|---|---|
| `KRAKEN_API_KEY` | private REST calls, `streams.private`, `trading_ws` | Kraken API key. |
| `KRAKEN_PRIVATE_KEY` | private REST calls, `streams.private`, `trading_ws` | Kraken private key, used to sign requests. |

Both are read by `Kraken.new()` when `api_key`/`private_key` aren't passed directly, and
are unused entirely when the client is built with `public=True`. See
[API Keys Setup](../api-keys.md) for where to generate them.

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
