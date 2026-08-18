"""`spot.account.trade_balance` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class TradeBalance(TypedDict):
  """Summary of collateral balances, margin position valuations, equity, and margin level."""

  eb: NotRequired[str]
  """Equivalent balance (combined balance of all currencies)."""
  tb: NotRequired[str]
  """Trade balance (combined balance of all equity currencies)."""
  m: NotRequired[str]
  """Margin amount of open positions."""
  n: NotRequired[str]
  """Unrealized net profit/loss of open positions."""
  c: NotRequired[str]
  """Cost basis of open positions."""
  v: NotRequired[str]
  """Current floating valuation of open positions."""
  e: NotRequired[str]
  """Equity: trade balance plus unrealized net profit/loss."""
  mf: NotRequired[str]
  """Free margin: equity minus initial margin (maximum margin available to open new positions)."""
  mfo: NotRequired[str]
  """Margin free for orders: available margin that can be used for new orders."""
  ml: NotRequired[str | None]
  """Margin level: `(equity / initial margin) * 100`. Only present when margin positions are open."""
  uv: NotRequired[str]
  """Unexecuted value: value of unfilled and partially filled orders."""


validate_trade_balance = validator(TradeBalance)


class TradeBalanceEndpoint(RpcEndpoint):
  """`spot.account.trade_balance`."""

  async def trade_balance(
    self,
    *,
    asset: str | None = None,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
  ) -> TradeBalance:
    """Retrieve a summary of collateral balances, margin position valuations, equity and margin level.

    **API Key Permissions Required:** `Orders and trades - Query open orders & trades`

    Args:
      asset: Base asset used to determine balance.
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-trade-balance)
    """
    data = {}
    if asset is not None:
      data['asset'] = asset
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier

    return await self.authed_request(
      '/0/private/TradeBalance', data, validator=validate_trade_balance
    )
