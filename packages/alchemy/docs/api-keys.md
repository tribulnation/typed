# API Keys Setup

This page explains how to configure the Alchemy API key.

## Create API Credentials

Create an API key from the official Alchemy dashboard.

Before using them in production:

- enable only the permissions you actually need
- restrict IPs when the provider supports it
- use separate keys for development and production when possible

## Environment Variables

The recommended setup is environment variables:

```bash
export ALCHEMY_API_KEY="your_api_key"
```

No API secret, passphrase, wallet, or trading credential is used by this client.

## Direct Usage

You can also pass credentials directly:

```python
from typed_alchemy import Alchemy

async with Alchemy.new(
  api_key="your_api_key",
) as client:
  ...
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
- confirm the selected Alchemy app supports the network you are querying
- check [Error Handling](reference/error-handling.md) for the client error model
