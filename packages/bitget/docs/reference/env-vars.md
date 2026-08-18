# Environment Variables

```bash
BITGET_ACCESS_KEY=
BITGET_SECRET_KEY=
BITGET_PASSPHRASE=
```

Read by `Bitget.new()` when `access_key`/`secret_key`/`passphrase` aren't passed explicitly, and
required unless the client is built with `public=True`. One triple authenticates against
whichever surface (`client.classic` or `client.uta`) matches your account's actual mode. See
[API Keys Setup](../api-keys.md).
