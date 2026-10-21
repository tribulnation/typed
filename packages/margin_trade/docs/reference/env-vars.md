# Environment Variables

The client reads no environment variables on its own: you pass the private key to
`MarginTrade.new`. The examples in these docs read it from these variables:

```bash
# .env
MARGIN_TRADE_TESTNET_PRIVATE_KEY="your_master_private_key"
MARGIN_TRADE_TESTNET_AGENT_PRIVATE_KEY="your_agent_private_key"
```

| Variable | Holds | Used as |
| - | - | - |
| `MARGIN_TRADE_TESTNET_PRIVATE_KEY` | the master account's Ed25519 private key | `MarginTrade.new(key, mainnet=False)` |
| `MARGIN_TRADE_TESTNET_AGENT_PRIVATE_KEY` | an approved agent's private key (optional) | `MarginTrade.new(agent_key, vault=master_address, mainnet=False)` |

Either key may be a hex 32-byte seed (`0x` optional), a base58 64-byte Solana secret key or
a base58 32-byte seed; see [Authenticated Setup](../authenticated-setup.md) for every format
`Wallet.parse` accepts.

## Guidance

1. Keep keys in an untracked `.env` file and load it explicitly (for example with
   `python-dotenv`).
2. Use separate keys for testnet and mainnet. The `mainnet` switch picks the host and the
   network code signed into every request together, so a signed request is only ever valid
   on the network you chose.
3. Prefer an agent key for trading bots: it can trade but cannot withdraw or manage
   agents.
