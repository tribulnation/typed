# How To

Task-focused guides for the most common workflows.

- [Fetch Market Data](fetch-market-data.md) — public prices, order books, and candles
- [Listen To Streams](listen-to-streams.md) — subscribe to market data and account event streams
- [Place & Manage Orders](place-and-manage-orders.md) — submit, query, cancel, and list spot orders
- [Fetch Account Data](manage-account-data.md) — balances, positions, and trade history
- [Query & Manage Earn Instruments](manage-earn.md) — Simple Earn products, positions, subscribe, and redeem
- [Manage Deposits & Withdrawals](manage-deposits-and-withdrawals.md) — deposit addresses/history and withdrawals
- [Paginate Through Results](paginate-through-results.md) — walk a time range across multiple pages

These guides use the spot surface (`client.spot`, `client.streams`, `client.ws_api`) as the
common case. USD-M futures (`client.usdm_futures`), COIN-M futures (`client.coinm_futures`),
and options (`client.options`) mirror `client.spot`'s `market`/`trading`/`account` shape on
their own hosts. Portfolio margin (`client.portfolio_margin`) only exposes `account` and
`trading` — it has no market data of its own.
