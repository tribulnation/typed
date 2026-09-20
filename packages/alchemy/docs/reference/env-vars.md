# Environment Variables

This page lists the environment variables used by the client.

## Standard Variables

Typed Alchemy uses one environment variable:

```bash
ALCHEMY_API_KEY=
```

## Guidance

- keep local values in an untracked `.env` file if needed
- load them explicitly in scripts and notebooks
- document any non-obvious required variables here

## HTTP Proxy Environment

| Variable | Description |
| --- | --- |
| `HTTP_PROXY` | Proxy URL for HTTP destinations. |
| `HTTPS_PROXY` | Proxy URL for HTTPS destinations. |
| `ALL_PROXY` | Fallback proxy URL when a scheme-specific variable is absent. |
| `NO_PROXY` | Comma-separated hosts or URLs that bypass environment proxies. |

HTTPX reads these by default. See [HTTP Timeouts and Proxies](async-usage.md#http-timeouts-and-proxies)
for explicit proxy configuration and `trust_env=False`.
