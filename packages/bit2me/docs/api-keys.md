# API Keys Setup

This page explains how to configure credentials for authenticated router usage.

## Create API Credentials

Create API credentials from the Bit2Me API management page:

<https://app.bit2me.com/profile/api>

Before using them in production:

- enable only the permissions you actually need
- restrict IPs when the provider supports it
- keep trading and withdrawal permissions separate when possible

## Environment Variables

The recommended setup is environment variables:

```bash
export BIT2ME_API_KEY="your_api_key"
export BIT2ME_SECRET_KEY="your_secret_key"
```

Those are the two variables currently used by `Bit2Me.new()` and the authenticated router helpers.

## Direct Usage

You can also pass credentials directly:

```python
from bit2me import Bit2Me

async with Bit2Me.new(
  api_key="your_api_key",
  api_secret="your_secret_key",
) as client:
  balances = await client.v1.trading.balance()
```

## Security Notes

- never commit credentials to git
- prefer read-only keys for development
- use separate keys for production automation
- rotate credentials after any suspected leak

## Troubleshooting

If authenticated requests fail:

- confirm the key has the required permissions
- confirm your environment variables are loaded
- check [Error Handling](reference/error-handling.md) for the client error model
