# Typed Etherscan

> A fully typed, validated async client for the Etherscan API.

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:  # reads ETHERSCAN_API_KEY from the environment
  balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
  print(balance)
```

## Why Typed Etherscan?

- **🎯 Precise Types**: `Literal` request parameters (`module`, `action`, `closest`, ...) so a typo is caught before the call leaves your machine.
- **✅ Runtime Validation**: every response is validated against Etherscan's own `status`/`message`/`result` envelope by default.
- **⚡ Async First**: async HTTP built on `httpx`, with a client-side rate limit for Etherscan's strict free-tier cap.
- **📚 Full Surface**: all 88 documented Etherscan V2 endpoints — account, blocks, contracts, gas tracker, logs, raw proxy RPC, stats, tokens, transactions, and usage — across every chain the V2 API supports.

## Installation

```bash
pip install typed-etherscan
```

## Documentation

- [**API Keys Setup**](api-keys.md) — get an Etherscan API key and configure it
- [**How To**](how-to/index.md) — task-focused guides for common queries
- [**Reference**](reference/index.md) — error handling, environment variables, async usage, timestamps
