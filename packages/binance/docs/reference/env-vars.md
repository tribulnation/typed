# Environment Variables

| Variable | Description |
| --- | --- |
| `BINANCE_API_KEY` | Binance API key. Required for authenticated (signed) calls. |
| `BINANCE_SECRET_KEY` | HMAC secret paired with the API key. Required for authenticated calls. |

Both are read automatically by `Binance.new()`. Pass `api_key`/`secret_key` directly to override
them, or `public=True` to build a client that only uses public endpoints and needs neither.

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
