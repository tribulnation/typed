# Environment Variables

This page lists the environment variables currently used by the authenticated Bit2Me router helpers.

## Used Variables

```bash
BIT2ME_API_KEY=
BIT2ME_SECRET_KEY=
```

`Bit2Me.new()` and `AuthEndpoint.new()` read those names from the environment when you do not pass credentials explicitly.

## Notes

- there is no separate passphrase or account-id env var in the current implementation
- public-only calls can use `Bit2Me.public()` instead of env vars
- if you want to switch hosts manually, pass `base_url=...` to the relevant constructor instead of relying on an env var

- keep local values in an untracked `.env` file if needed
- load them explicitly in scripts and notebooks
