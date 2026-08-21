# Environment Variables

## Public Usage

No environment variables are required for public reads or public streams.

## Authenticated Mainnet Usage

Use `HYPERLIQUID_PRIVATE_KEY` when you construct an authenticated mainnet client without passing a wallet explicitly:

```bash
HYPERLIQUID_PRIVATE_KEY=
```

`Hyperliquid.new()` reads `HYPERLIQUID_PRIVATE_KEY` by default.

## Authenticated Testnet Usage

Use `HYPERLIQUID_TESTNET_PRIVATE_KEY` when you construct an authenticated testnet client without passing a wallet explicitly:

```bash
HYPERLIQUID_TESTNET_PRIVATE_KEY=
```

`Hyperliquid.new(mainnet=False)` reads `HYPERLIQUID_TESTNET_PRIVATE_KEY`.

## Networks

Network selection is configured through constructor arguments:

```python
from typed_hyperliquid import Hyperliquid

client = Hyperliquid.new(mainnet=False)
```

There is no API key, API secret, or passphrase flow in the current implementation.
