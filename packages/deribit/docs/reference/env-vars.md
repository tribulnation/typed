# Environment Variables

`Deribit.new()` reads these when `client_id`/`client_secret` aren't passed directly.

```bash
DERIBIT_CLIENT_ID=
DERIBIT_CLIENT_SECRET=
```

`Deribit.new(testnet=True)` reads the `TEST_`-prefixed pair instead:

```bash
TEST_DERIBIT_CLIENT_ID=
TEST_DERIBIT_CLIENT_SECRET=
```

Neither pair is read for a `Deribit.new(public=True)` client — public methods and public
channel subscriptions need no credentials at all.
