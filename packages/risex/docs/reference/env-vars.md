# Environment Variables

`RISEx.new()` reads these when no key is passed as an argument. None is needed for `RISEx.new(public=True)`.

| Variable | Value | Needed for |
| --- | --- | --- |
| `RISEX_ACCOUNT_KEY` | the account wallet's private key, hex | registering or revoking signers, OperatorHub allowances; can also log in |
| `RISEX_SIGNER_KEY` | the registered signer (session) key, hex | orders, cancels, leverage and margin changes, logins, account streams |
| `RISEX_ACCOUNT` | the account address | a signer-only setup (no `RISEX_ACCOUNT_KEY`) |

At least one key must be set. With both keys set, `RISEX_ACCOUNT` is optional and, if present, must match the account key's address.

```bash
# .env, full setup
RISEX_ACCOUNT_KEY="0x..."
RISEX_SIGNER_KEY="0x..."

# .env, trading only
RISEX_SIGNER_KEY="0x..."
RISEX_ACCOUNT="0xYourAccountAddress"
```

The client does not load `.env` files itself; use `python-dotenv` or your process manager.

Keys passed to `RISEx.new(account_key=..., signer_key=..., account=...)` replace the environment entirely: if either key is passed, none of the variables is read.

The network is not an environment variable: pass `network='testnet'` or `network='mainnet'` (the default) to `RISEx.new()`.
