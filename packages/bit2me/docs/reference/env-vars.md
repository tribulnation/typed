# Environment Variables

```bash
BIT2ME_API_KEY=
BIT2ME_SECRET_KEY=
```

`Bit2Me.new()` reads these when `api_key`/`api_secret` aren't passed explicitly. `Bit2Me.new(public=True)` needs neither.

## Notes

- there is no separate passphrase, account id, or WS-specific credential; the same API key/secret pair authenticates `client.http`, `client.trading_ws`, and `client.crypto_ws`
- to point at a different host (e.g. for tests against a mock), pass `base_url=`/`trading_ws_url=`/`crypto_ws_url=` to `Bit2Me.new()` directly rather than an env var
