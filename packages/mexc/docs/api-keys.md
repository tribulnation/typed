# API Keys Setup

This page explains how to configure credentials for authenticated spot and futures requests.

## Create API Credentials

Create API credentials from the MEXC API management page:

<https://www.mexc.com/user/openapi>

Before using them in production:

1. Enable only the permissions you actually need.
2. Restrict IPs when the provider supports it.
3. Keep trading and withdrawal permissions separate when possible.

## Environment Variables

The recommended setup is environment variables:

```bash
export MEXC_ACCESS_KEY="your_access_key"
export MEXC_SECRET_KEY="your_secret_key"
```

Those are the only credential variables used by `MEXC.new()`, `Spot.new()`, and `Futures.new()`.

MEXC uses access key + secret key only. There is no passphrase in the current client model.

## Direct Usage

You can also pass credentials directly:

```python
from mexc import MEXC

async with MEXC.new(
  api_key="your_access_key",
  api_secret="your_secret_key",
) as client:
  account = await client.spot.account.info()
  print(account['accountType'])
```

## Security Notes

1. Never commit credentials to git, issue trackers, logs, notebooks, or shared terminals.
2. Prefer read-only keys for development and documentation examples.
3. Use separate keys for production automation, manual trading, and local experiments.
4. Keep withdrawal permission disabled unless the exact workflow requires it.
5. Keep futures trading permission separate from spot read access where your account setup allows it.
6. Restrict production keys by IP before enabling trading permission.
7. Rotate credentials after any suspected leak or after using them on an untrusted machine.
8. Keys without an IP whitelist expire after 90 days on MEXC.

## Troubleshooting

If authenticated requests fail:

1. Confirm the key has the required permissions.
2. Confirm your environment variables are loaded.
3. Confirm your IP whitelist configuration on the MEXC side.
4. Check [Error Handling](reference/error-handling.md) for the client error model.
