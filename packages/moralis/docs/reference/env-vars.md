# Environment Variables

```bash
MORALIS_API_KEY=
```

`MORALIS_API_KEY` is the only environment variable the client reads. It's picked up
automatically by `Moralis.new()` — see [API Keys Setup](../api-keys.md).

## Guidance

- keep local values in an untracked `.env` file
- load them explicitly in scripts and notebooks

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
