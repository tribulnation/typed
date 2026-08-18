# API Overview

The Bit2Me client surface is versioned.

The main authenticated entry point is:

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  ...
```

That gives you three versioned routers:

- `client.v1`
- `client.v2`
- `client.v3`

## `Bit2Me`

`Bit2Me` is the ergonomic authenticated router.

Use it when you want:

- authenticated trading and wallet flows
- account management
- earn, loan, teller, and signin operations
- one client object spanning multiple API versions

## `v1`

`v1` is the broadest surface right now. It includes routers such as:

- `account`
- `blockchain_manager`
- `currency`
- `earn`
- `loan`
- `misc`
- `signin`
- `social_pay`
- `teller`
- `trading`
- `verifier`
- `wallet`

Notable implemented areas include:

- `v1.trading.orders` for `create`, `get`, `list`, `cancel`, and `list_trades`
- `v1.trading.balance` and `v1.trading.wallets` for trading-wallet balances and transfers
- `v1.wallet.transactions` and `v1.wallet.pockets` for wallet operations

## `v2`

`v2` currently covers:

- `account`
- `currency`
- `earn`
- `loan`
- `trading`
- `wallet`

Notable implemented areas include:

- `v2.trading.tickers` and `v2.trading.order_book`
- `v2.wallet.transactions`
- `v2.wallet.pockets`
- `v2.earn.apy`, `v2.earn.assets`, and `v2.earn.wallets`

## `v3`

`v3` currently covers:

- `account`
- `currency`
- `signin`

This includes newer account and market-data style endpoints such as `v3.account.get`, `v3.currency.ticker`, and `v3.currency.chart`.

## Public vs Authenticated Access

This package mixes public and authenticated endpoints across the versioned modules.

For authenticated usage, prefer `Bit2Me.new()`.

For public-only usage, construct `Bit2Me.public()` and call the public routes through the versioned client surface.

## Current Limitation

The current package is HTTP-only.

WebSocket usage is not implemented in the public client surface yet.

## Generated Reference

The complete endpoint reference belongs under [Reference > API](reference/api/index.md).
