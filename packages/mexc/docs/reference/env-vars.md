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
