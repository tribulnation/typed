# Environment Variables

`Lighter.new()` reads these when the matching argument is not passed. The package reads
`os.environ` only: load a `.env` file yourself (for example with `python-dotenv`).

## Variables

| Variable | Argument | Needed for |
|---|---|---|
| `LIGHTER_ACCOUNT_INDEX` | `account_index` | the account your API key belongs to |
| `LIGHTER_API_KEY_INDEX` | `api_key_index` | the API key's slot (`4` to `254`) |
| `LIGHTER_API_PRIVATE_KEY` | `api_private_key` | the API key itself: transactions, signing, derived auth tokens |
| `LIGHTER_ETH_PRIVATE_KEY` | `eth_private_key` | optional: the few Ethereum-signed transactions |
| `LIGHTER_AUTH_TOKEN` | `auth_token` | optional: when no API key is set, a read-only `ro:` token, or a pre-signed standard token (never renewed; expires within 8 hours) |
| `LIGHTER_BRIDGE_API_KEY` | `bridge_api_key` | optional: `client.deposit_bridge` |

```bash
# .env
LIGHTER_ACCOUNT_INDEX="123"
LIGHTER_API_KEY_INDEX="4"
LIGHTER_API_PRIVATE_KEY="your_api_private_key"
```

With `LIGHTER_API_PRIVATE_KEY` set, `LIGHTER_AUTH_TOKEN` is ignored: the client derives its
own tokens from the key. Several API keys at once are passed as `api_keys={slot: key}`;
there is no environment form for them.

## Per-Network Prefixes

Each network reads its own variables, so mainnet and testnet credentials can live in one
`.env` side by side:

| `Lighter.new(network=...)` | Prefix | Example |
|---|---|---|
| `'mainnet'` (default) | `LIGHTER` | `LIGHTER_API_PRIVATE_KEY` |
| `'testnet'` | `LIGHTER_TESTNET` | `LIGHTER_TESTNET_API_PRIVATE_KEY` |
| `'robinhood'` | `LIGHTER_ROBINHOOD` | `LIGHTER_ROBINHOOD_API_PRIVATE_KEY` |
| `'robinhood-testnet'` | `LIGHTER_ROBINHOOD_TESTNET` | `LIGHTER_ROBINHOOD_TESTNET_API_PRIVATE_KEY` |

All six variables above take the prefix: `LIGHTER_TESTNET_ACCOUNT_INDEX`,
`LIGHTER_TESTNET_ETH_PRIVATE_KEY`, and so on.

See [Authenticated Setup](../authenticated-setup.md) for how to obtain each value.
