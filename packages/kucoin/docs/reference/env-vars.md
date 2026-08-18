# Environment Variables

| Variable | Required | Description |
|---|---|---|
| `KUCOIN_API_KEY` | for authenticated use | KuCoin API key. |
| `KUCOIN_API_SECRET` | for authenticated use | KuCoin API secret. |
| `KUCOIN_API_PASSPHRASE` | for authenticated use | KuCoin API passphrase, set when the key was created. |

All three fall back to a constructor argument of the same name
(`KuCoin.new(api_key=..., api_secret=..., api_passphrase=...)`), and all three are
skipped entirely for a `KuCoin.new(public=True)` client. None are read from anywhere but
the environment or the constructor call — keep them in an untracked `.env` file or your
process's own secret store.
