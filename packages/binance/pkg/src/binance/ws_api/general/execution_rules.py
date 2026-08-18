from json import dumps
from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class ExecutionRule(TypedDict):
  """One execution rule. Only `PRICE_RANGE` is documented, bounding bid/ask price as a multiple of a reference price."""

  ruleType: str
  """Execution rule type. Only `PRICE_RANGE` is documented; not declared as a closed set (see notes)."""
  bidLimitMultUp: str
  """Maximum multiple of the reference price a bid price may exceed."""
  bidLimitMultDown: str
  """Minimum multiple of the reference price a bid price may fall below."""
  askLimitMultUp: str
  """Maximum multiple of the reference price an ask price may exceed."""
  askLimitMultDown: str
  """Minimum multiple of the reference price an ask price may fall below."""


class SymbolExecutionRules(TypedDict):
  """Execution rules for one symbol."""

  symbol: str
  """Symbol."""
  rules: list[ExecutionRule]
  """Execution rules in effect for this symbol."""


class ExecutionRules(TypedDict):
  """Execution rules keyed by symbol."""

  symbolRules: list[SymbolExecutionRules]
  """Execution rules for each symbol in scope."""


class ExecutionRulesEndpoint(WsRpcEndpoint):
  """Query execution rules"""

  async def execution_rules(
    self,
    *,
    symbol: str | None = None,
    symbols: list[str] | None = None,
    symbol_status: Literal['TRADING', 'HALT', 'BREAK'] | None = None,
    validate: bool | None = None,
  ) -> ExecutionRules:
    """Query symbol price-band execution rules (e.g. permitted bid/ask deviation from a reference price). No combination of multiple parameters is allowed.

    Args:
      symbol: Query for the specified symbol.
      symbols: Query for multiple symbols.
      symbol_status: Query for all symbols with the specified trading status.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#query-execution-rules)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if symbols is not None:
      params['symbols'] = dumps(symbols, separators=(',', ':'))
    if symbol_status is not None:
      params['symbolStatus'] = symbol_status
    _Response = ExecutionRules
    _validator = validator[_Response](_Response)
    return await self.request(
      'executionRules', params=params, validator=_validator, validate=validate
    )
