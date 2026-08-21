# Typed Etherscan

> A fully typed, validated async client for the Etherscan API

<p align="center">
  <a href="https://pypi.org/project/typed-etherscan/">
    <img src="https://img.shields.io/pypi/v/typed-etherscan.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-etherscan/">
    <img src="https://img.shields.io/pypi/pyversions/typed-etherscan.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/etherscan">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-etherscan.svg" alt="License">
  </a>
</p>

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

- [**API Keys Setup**](https://tribulnation.com/typed/etherscan/api-keys) — get an Etherscan API key and configure it
- [**How To**](https://tribulnation.com/typed/etherscan/how-to) — task-focused guides for common queries
- [**Reference**](https://tribulnation.com/typed/etherscan/reference) — error handling, environment variables, async usage, timestamps

## License

MIT — see [LICENSE](LICENSE).
