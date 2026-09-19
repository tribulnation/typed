# Environment Variables

```bash
BIT2ME_API_KEY=
BIT2ME_SECRET_KEY=
```

`Bit2Me.new()` reads these when `api_key`/`api_secret` aren't passed explicitly. `Bit2Me.new(public=True)` needs neither.

## Notes

- there is no separate passphrase, account id, or WS-specific credential; the same API key/secret pair authenticates `client.http`, `client.trading_ws`, and `client.crypto_ws`
- to point at a different host (e.g. for tests against a mock), pass `base_url=`/`trading_ws_url=`/`crypto_ws_url=` to `Bit2Me.new()` directly rather than an env var

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
