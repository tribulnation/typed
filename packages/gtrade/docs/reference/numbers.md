# Numbers & Precision

gTrade's services encode numbers differently, and the client keeps each one as the service
sends it rather than normalizing:

| Surface | Prices, sizes, amounts | In Python |
| - | - | - |
| `client.trading` | Decimal strings | `Decimal`, exact |
| `client.backend` | Integer strings at contract precision | `int`, unscaled |
| `client.backend_global` | JSON numbers (referral USD amounts: decimal strings) | `float` (referral amounts: `Decimal`) |
| `client.pricing` | JSON numbers | `float` |

## Trading API

Every price, size, rate and USD amount is a `Decimal` built from the API's own string, so
nothing is lost to floating point. Request decimals accept `Decimal` or `str` and are sent
in plain notation (never `1E-7`). Rates are fractions (`0.00035` = 0.035%), except
`slippage`, which is in percent (`1` = 1%).

## Per-Chain Backend

The backend republishes contract storage as is: integer strings scaled by the contract's
fixed-point precision, decoded to `int` without rescaling. Divide by the field's precision
to get the real value:

| Kind of value | Precision |
| - | - |
| Prices (`openPrice`, `tp`, `sl`, ...) | 1e10 |
| Leverage | 1e3 |
| Percentages (`spreadP`, fee `P` fields, ...) | 1e10 or 1e3, depending on the field |
| Collateral amounts | The collateral token's decimals (6 for USDC, 18 for DAI) |
| Position size in the traded asset (`positionSizeToken`) | 1e18 |

Every field's docstring states its precision, so your editor shows it on hover.

```python
from decimal import Decimal
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  for container in await client.backend.trades.open():
    trade = container['trade']
    price = Decimal(trade['openPrice']) / 10**10
    leverage = Decimal(trade['leverage']) / 10**3
```

A few backend values that the backend has already converted (collateral USD prices, for
example) are plain floats, and the `new_trade_history()` stream pushes records whose prices
and amounts are already normalized JSON numbers. The Trading API serves markets, positions and orders already
scaled, so prefer `client.trading` when you don't need raw contract values.

## Backend Global & Pricing

Both send JSON numbers, decoded as `float`: fine for display and analytics, not for exact
accounting. Pricing snapshots are arrays indexed by `pairIndex`, with `None` for a pair
that has no price; stream batches are flat `[pairIndex, price, ...]` arrays.

Backend Global's referral USD amounts are the exception: they arrive as decimal strings and
decode as `Decimal`; micro-USDC amounts are integers (divide by 1e6).
