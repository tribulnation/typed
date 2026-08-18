from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMPositionMarginChange(TypedDict):
  """One margin add/reduce event."""

  amount: str
  """Margin amount changed."""
  asset: str
  """Margin asset."""
  symbol: str
  """Symbol."""
  time: int
  """Event time."""
  type: Literal[1, 2]
  """1: margin was added, 2: margin was reduced."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side. `BOTH` for One-way Mode; `LONG` or `SHORT` for Hedge Mode."""


class GetPositionMarginChangeHistory(RpcEndpoint):
  """Get Position Margin Change History"""

  async def get_position_margin_change_history(
    self,
    *,
    symbol: str,
    type: Literal[1, 2] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[CoinMPositionMarginChange]:
    """Get the history of isolated-margin add/reduce actions on a symbol.

    Args:
      symbol: Symbol.
      type: 1: Add position margin, 2: Reduce position margin.
      start_time: Start time.
      end_time: End time.
      limit: Maximum number of records to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#get-position-margin-change-history)
    """
    params: dict = {
      'symbol': symbol,
    }
    if type is not None:
      params['type'] = type
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    _Response = list[CoinMPositionMarginChange]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/dapi/v1/positionMargin/history',
      params=params,
      validator=_validator,
      validate=validate,
    )
