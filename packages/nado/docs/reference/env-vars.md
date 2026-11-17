# Environment Variables

`Nado.new()` reads credentials from the environment when you don't pass them as arguments.
Each network has its own prefix, so a testnet key is never used on mainnet.

| Variable | Network | Meaning |
| --- | --- | --- |
| `NADO_PRIVATE_KEY` | mainnet | Signing key (hex): the wallet's own, or its linked signer's |
| `NADO_ADDRESS` | mainnet | Owner wallet address, when the key is a linked signer; defaults to the key's address |
| `NADO_SUBACCOUNT` | mainnet | Subaccount name; defaults to `default` |
| `NADO_TESTNET_PRIVATE_KEY` | testnet | Same, for `network='testnet'` |
| `NADO_TESTNET_ADDRESS` | testnet | Same, for `network='testnet'` |
| `NADO_TESTNET_SUBACCOUNT` | testnet | Same, for `network='testnet'` |

Only the private key is needed to sign. None of them are needed with `public=True`.

```bash
# .env
NADO_PRIVATE_KEY="0x..."
NADO_TESTNET_PRIVATE_KEY="0x..."
```

```python
from dotenv import load_dotenv
from typed_nado import Nado

load_dotenv()

mainnet = Nado.new()                   # NADO_PRIVATE_KEY, NADO_ADDRESS, NADO_SUBACCOUNT
testnet = Nado.new(network='testnet')  # NADO_TESTNET_*
```

Passing `private_key=` explicitly ignores all three variables: `address` then defaults to
the key's own address and `subaccount` to `default`, unless you pass them too.
