# Environment Variables

`Deribit.new()` reads these when `client_id`/`client_secret` aren't passed directly.

```bash
DERIBIT_CLIENT_ID=
DERIBIT_CLIENT_SECRET=
```

`Deribit.new(testnet=True)` reads the `TEST_`-prefixed pair instead:

```bash
TEST_DERIBIT_CLIENT_ID=
TEST_DERIBIT_CLIENT_SECRET=
```

Neither pair is read for a `Deribit.new(public=True)` client — public methods and public
channel subscriptions need no credentials at all.

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
