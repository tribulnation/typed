# Environment Variables

This page lists the environment variables currently used by the MEXC client constructors.

## Used Variables

```bash
MEXC_ACCESS_KEY=
MEXC_SECRET_KEY=
```

## Guidance

- `MEXC.new()`, `Spot.new()`, `Futures.new()`, and both stream constructors read these names when credentials are not passed explicitly
- public-only calls can use `MEXC.new(public=True)`, `Spot.new(public=True)`, or `Futures.new(public=True)`
- keep local values in an untracked `.env` file if needed
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
