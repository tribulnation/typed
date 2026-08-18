from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMModifyIsolatedPositionMarginResult(TypedDict):
  """The margin change that was applied."""

  amount: float
  """Margin amount that was added or reduced."""
  code: int
  """Result code."""
  msg: str
  """Result message."""
  type: Literal[1, 2]
  """1: margin was added, 2: margin was reduced."""


class ModifyIsolatedPositionMargin(RpcEndpoint):
  """Modify Isolated Position Margin"""

  async def modify_isolated_position_margin(
    self,
    *,
    symbol: str,
    amount: float,
    type: Literal[1, 2],
    position_side: Literal['BOTH', 'LONG', 'SHORT'] | None = None,
    validate: bool | None = None,
  ) -> CoinMModifyIsolatedPositionMarginResult:
    """Add or reduce margin on an isolated-margin position.

    Args:
      symbol: Symbol.
      amount: Margin amount, in the margin asset.
      type: 1: Add position margin, 2: Reduce position margin.
      position_side: Default `BOTH` for One-way Mode; `LONG` or `SHORT` for Hedge Mode. Must be sent in Hedge Mode.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#modify-isolated-position-margin)
    """
    params: dict = {
      'symbol': symbol,
      'amount': amount,
      'type': type,
    }
    if position_side is not None:
      params['positionSide'] = position_side
    _Response = CoinMModifyIsolatedPositionMarginResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/dapi/v1/positionMargin',
      params=params,
      validator=_validator,
      validate=validate,
    )
