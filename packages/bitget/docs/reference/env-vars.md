# Environment Variables

```bash
BITGET_ACCESS_KEY=
BITGET_SECRET_KEY=
BITGET_PASSPHRASE=
```

Read by `Bitget.new()` when `access_key`/`secret_key`/`passphrase` aren't passed explicitly, and
required unless the client is built with `public=True`. One triple authenticates against
whichever surface (`client.classic` or `client.uta`) matches your account's actual mode. See
[API Keys Setup](../api-keys.md).

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
