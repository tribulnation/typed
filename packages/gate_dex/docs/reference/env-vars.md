# Environment Variables

`GateDex.new()` reads its credentials from these variables when the matching argument is not
passed. Both are required: Gate DEX has no public endpoints.

| Variable | Argument | Holds |
| --- | --- | --- |
| `GATE_DEX_API_KEY` | `api_key` | the API Key (AK) |
| `GATE_DEX_SECRET_KEY` | `api_secret` | the Secret Key (SK) |

```bash
# .env
GATE_DEX_API_KEY="your_api_key"
GATE_DEX_SECRET_KEY="your_secret_key"
```

The key's passphrase is not needed: it only protects viewing the Secret Key in Gate's
console. If either variable is missing and no argument is passed, `GateDex.new()` raises
`AuthError`.

See [API Keys Setup](../api-keys.md) for how to create a key.
