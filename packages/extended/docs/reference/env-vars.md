# Environment Variables

`Extended.new()` reads credentials from these variables when the matching argument is not
passed. Mainnet uses the `EXTENDED_` prefix, `network='testnet'` the `EXTENDED_TESTNET_` prefix.

| Mainnet | Testnet | Argument | Needed for |
| --- | --- | --- | --- |
| `EXTENDED_API_KEY` | `EXTENDED_TESTNET_API_KEY` | `api_key` | every private call |
| `EXTENDED_STARK_PRIVATE_KEY` | `EXTENDED_TESTNET_STARK_PRIVATE_KEY` | `stark_private_key` | orders, transfers, withdrawals |
| `EXTENDED_VAULT` | `EXTENDED_TESTNET_VAULT` | `vault` | required with the Stark private key |
| `EXTENDED_STARK_PUBLIC_KEY` | `EXTENDED_TESTNET_STARK_PUBLIC_KEY` | `stark_public_key` | optional; checked against the private key |

Keys are hex (`0x...`); the vault is a decimal or hex integer. With `public=True` no variable
is read.

```bash
# .env
EXTENDED_API_KEY="your_api_key"
EXTENDED_STARK_PRIVATE_KEY="0x..."
EXTENDED_VAULT="123456"
```

See [Authenticated Setup](../authenticated-setup.md) for where to find each value.
