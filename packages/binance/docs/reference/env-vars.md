# Environment Variables

| Variable | Description |
| --- | --- |
| `BINANCE_API_KEY` | Binance API key. Required for authenticated (signed) calls. |
| `BINANCE_SECRET_KEY` | HMAC secret paired with the API key. Required for authenticated calls. |

Both are read automatically by `Binance.new()`. Pass `api_key`/`secret_key` directly to override
them, or `public=True` to build a client that only uses public endpoints and needs neither.
