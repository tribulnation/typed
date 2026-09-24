# Environment Variables

`Aster.new()` reads these when the matching argument is not passed. Arguments always take
precedence. `Aster.new(public=True)` reads none of them.

| Variable | Argument | Meaning |
| --- | --- | --- |
| `ASTER_USER` | `user` | Main wallet address: your Aster account. Optional when `ASTER_USER_PRIVATE_KEY` is set. |
| `ASTER_SIGNER_PRIVATE_KEY` | `signer` | API wallet (agent) private key. Signs trading and account requests. |
| `ASTER_SIGNER` | | API wallet address. Optional; when set, it must match `ASTER_SIGNER_PRIVATE_KEY`. |
| `ASTER_USER_PRIVATE_KEY` | `main` | Main wallet private key. Optional; needed only for agent, builder and sub-account management, Aster Chain transfers and staking, and EVM withdrawals. |

```bash
ASTER_USER="0x...main-wallet-address"
ASTER_SIGNER="0x...api-wallet-address"
ASTER_SIGNER_PRIVATE_KEY="0x...api-wallet-private-key"
ASTER_USER_PRIVATE_KEY="0x...main-wallet-private-key"
```

The same names are read on mainnet and testnet (`mainnet=False`), so keep separate `.env`
files per network.

`Aster.new()` raises `AuthError` when neither private key is available, when no account address
can be determined, or when an address does not match its key. A call that needs the main
wallet raises `AuthError` before sending if `ASTER_USER_PRIVATE_KEY` was not provided.

Keep these values in an untracked `.env` file and load them with `python-dotenv` or your
process manager.
