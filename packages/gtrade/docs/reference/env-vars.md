# Environment Variables

`GTrade.new()` reads two optional variables:

| Variable | Value | Used for |
| - | - | - |
| `GTRADE_AGENT_PRIVATE_KEY` | The agent's EVM private key, hex | Signing private requests, private channels and writes |
| `GTRADE_API_KEY` | A read-only Trading API key (`gk_...`) | Private reads and private channels |

```bash
GTRADE_AGENT_PRIVATE_KEY="0x..."
GTRADE_API_KEY="gk_..."
```

- At least one is needed unless the client is built with `public=True`, which reads neither
  and raises `ValueError` if given a credential.
- Arguments replace the environment as a whole: passing `agent` or `api_key` to
  `GTrade.new()` reads neither variable. `agent` also accepts an `eth_account`
  `LocalAccount`.
- With both set, private reads use the API key and writes use the agent.

With a separate agent, the trader's master key is only needed to sign the one-off
registration, and never by the client. If you register the trader's own wallet as its
agent, `GTRADE_AGENT_PRIVATE_KEY` is the master key. See
[Wallet & Agent Setup](../authenticated-setup.md) for how both credentials are created and
the trade-off between the two setups.

The client reads the process environment only; load a `.env` file yourself, for example
with `python-dotenv`.

## Service URLs

No URL comes from the environment. To send a service's traffic elsewhere, such as a
self-hosted proxy or a local test server, pass `urls` to `GTrade.new()`. Each key replaces
one default; the others keep the chain's:

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True, urls={
  'pricing': 'http://localhost:8080',      # a local test server
  'pricing_ws': 'ws://localhost:8080/v3',
}) as client:
  charts = await client.pricing.snapshots.charts()
```

| Key | Replaces |
| - | - |
| `trading` | The Trading API chain root, `https://api.gains.trade/v1/{chain}` |
| `trading_host` | The Trading API host for `system.health` and `system.ready`, `https://api.gains.trade` |
| `trading_ws` | The Trading API WebSocket, `wss://api.gains.trade/v1/{chain}/ws` |
| `backend` | The per-chain backend, `https://backend-{chain}.gains.trade` |
| `backend_ws` | The per-chain backend's event stream, `wss://backend-{chain}.gains.trade` |
| `backend_global` | Backend Global, `https://backend-global.gains.trade` |
| `pricing` | Pricing, `https://backend-pricing.eu.gains.trade` |
| `pricing_ws` | The price stream, `wss://backend-pricing.eu.gains.trade/v3` |

(`arbitrum-sepolia` uses `api-testnet.gains.trade` and `backend-sepolia.gains.trade`.)

Agent signatures cover the request path the client sends, so a Trading API proxy must not
rewrite it: pass a URL whose path is the one the API receives (`/v1/{chain}`, and
`/v1/{chain}/ws` for the WebSocket), or the API rejects the signature with an `AuthError`.
