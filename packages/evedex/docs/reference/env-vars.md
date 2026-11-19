# Environment Variables

`Evedex.new()` reads credentials from the environment when they are not passed as
arguments. The prefix depends on the environment: `EVEDEX_` for production (`env='prod'`,
the default) and `EVEDEX_DEMO_` for the demo environment (`env='demo'`).

| Production | Demo | Purpose |
| --- | --- | --- |
| `EVEDEX_PRIVATE_KEY` | `EVEDEX_DEMO_PRIVATE_KEY` | Wallet private key (hex). Signs in, signs orders and other actions, opens private channels. |
| `EVEDEX_API_KEY` | `EVEDEX_DEMO_API_KEY` | API key for read-only private Exchange REST calls. |
| `EVEDEX_ADDRESS` | `EVEDEX_DEMO_ADDRESS` | Optional. Expected wallet address, checked against the private key. |

At least one of the private key or the API key is required unless you build the client with
`public=True`; otherwise `Evedex.new()` raises `AuthError`. Explicit arguments
(`private_key=`, `api_key=`, `address=`) take precedence over the variables.

```bash
# .env
EVEDEX_PRIVATE_KEY="0x..."
EVEDEX_API_KEY="your_api_key"
```

The client does not load `.env` files itself; use `python-dotenv` or export the variables
in your shell:

```python
from dotenv import load_dotenv
from typed_evedex import Evedex

load_dotenv()

async with Evedex.new() as client:
  me = await client.exchange.account.me()
```
