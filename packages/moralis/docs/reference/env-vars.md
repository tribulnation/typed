# Environment Variables

```bash
MORALIS_API_KEY=
```

`MORALIS_API_KEY` is the only environment variable the client reads. It's picked up
automatically by `Moralis.new()` — see [API Keys Setup](../api-keys.md).

## Guidance

- keep local values in an untracked `.env` file
- load them explicitly in scripts and notebooks
