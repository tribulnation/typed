# API Keys Setup

Every Moralis call needs an API key. Create one from the Moralis dashboard's API keys
page, then make it available to the client.

## Environment Variables

The recommended setup is an environment variable:

```bash
export MORALIS_API_KEY="your_api_key"
```

With `MORALIS_API_KEY` set, `Moralis.new()` picks it up automatically:

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  ...
```

## Direct Usage

You can also pass the key directly:

```python
from typed_moralis import Moralis

async with Moralis.new('your_api_key') as client:
  ...
```

## Troubleshooting

If requests fail with an authentication error:

- confirm `MORALIS_API_KEY` is set, or that you passed a key explicitly
- confirm the key hasn't hit its daily request allowance
- check [Error Handling](reference/error-handling.md) for the client's error model
