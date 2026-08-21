"""dYdX indexer enums types and endpoint."""

from typing_extensions import Literal

PositionSide = Literal['LONG', 'SHORT']
OrderSide = Literal['BUY', 'SELL']

OrderStatus = Literal[
  'OPEN',
  'FILLED',
  'CANCELED',
  'BEST_EFFORT_CANCELED',
  'UNTRIGGERED',
  'BEST_EFFORT_OPENED',
  'PENDING',
]

OrderType = Literal[
  'LIMIT',
  'MARKET',
  'STOP_LIMIT',
  'STOP_MARKET',
  'TRAILING_STOP',
  'TAKE_PROFIT',
  'TAKE_PROFIT_MARKET',
  'HARD_TRADE',
  'FAILED_HARD_TRADE',
  'TRANSFER_PLACEHOLDER',
]
"""
`LIMIT`: Executes at a specified price or better.
`MARKET`: Executes immediately at the best available price.
`STOP_LIMIT`: Becomes a limit order once a stop price is reached.
`STOP_MARKET`: Becomes a market order once a stop price is reached.
`TRAILING_STOP`: A dynamic stop order that adjusts based on market movement.
`TAKE_PROFIT`: A limit order to secure profits once a target price is reached.
`TAKE_PROFIT_MARKET`: A market order to secure profits once a target price is reached.
`HARD_TRADE`: A special internal trade type, typically used in matching engines.
`FAILED_HARD_TRADE`: Represents a failed execution of a HardTrade.
`TRANSFER_PLACEHOLDER`: A placeholder type used internally for transfers.
"""

TimeInForce = Literal['GTT', 'IOC', 'FOK']
Liquidity = Literal['MAKER', 'TAKER']
FillType = Literal['LIMIT', 'LIQUIDATED', 'LIQUIDATION', 'DELEVERAGED', 'OFFSETTING']
"""
`LIMIT`: Result of a regular limit order.
`LIQUIDATED`: Result of liquidating another trader's position.
`LIQUIDATION`: Result of one's own position being liquidated.
`DELEVERAGED`: Caused by automatic deleveraging in risk management.
`OFFSETTING`: Result of offsetting positions, often for risk reduction.
"""

TransferType = Literal['TRANSFER_IN', 'TRANSFER_OUT', 'DEPOSIT', 'WITHDRAWAL']
