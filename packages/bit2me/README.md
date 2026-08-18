# Typed Bit2Me

> Fully typed, validated async client for the Bit2Me API: REST trading, wallet, and earn, plus both Bit2Me WebSocket surfaces.

**Use autocomplete instead of documentation.**

```python
from dotenv import load_dotenv
from bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0].get('currency'), balances[0].get('balance'))
```

## Why Typed Bit2Me?

- **🎯 Precise Types**: literal types for order sides, order types, and statuses; `Decimal` for prices and amounts; a full `TypedDict` per response.
- **✅ Runtime Validation**: every REST response and every WebSocket push is validated against its documented schema by default.
- **⚡ Async First**: async HTTP plus two independent WebSocket surfaces (the Trading Spot socket for order commands and channel subscriptions, and the account-notifications socket), built for concurrent trading workflows.
- **📚 Full Surface**: the complete `v1`/`v2`/`v3` REST surface (trading, wallet, account, earn, and more), not just tickers.

## Installation

```bash
pip install typed-bit2me
```

## Documentation

- [**Getting Started**](https://tribulnation.com/typed/bit2me/getting-started): install the package and configure credentials
- [**How To**](https://tribulnation.com/typed/bit2me/how-to): task-focused guides for market data, streams, orders, accounts, earn, and funds
- [**Reference**](https://tribulnation.com/typed/bit2me/reference): async usage, error handling, and environment variables
