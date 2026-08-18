from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMLeverageBracket(TypedDict):
  """One notional bracket."""

  bracket: int
  """Bracket number."""
  initialLeverage: int
  """Maximum leverage available for this bracket."""
  qtyCap: int
  """Upper edge of this bracket's base asset quantity range."""
  qtylFloor: int
  """Lower edge of this bracket's base asset quantity range."""
  maintMarginRatio: float
  """Maintenance margin ratio for this bracket."""
  cum: float
  """Auxiliary number for quick calculation of maintenance amount within this bracket."""


class CoinMPairLeverageBracketGroup(TypedDict):
  """Notional brackets for one pair."""

  pair: str
  """Trading pair."""
  brackets: list[CoinMLeverageBracket]
  """Notional brackets, ordered from lowest to highest."""


class LeverageBracketByPair(RpcEndpoint):
  """Get a pair's default notional bracket list (v1). Not recommended for continued use: with multiple symbols under one pair carrying different brackets, this can return ambiguous values — prefer the symbol-based v2 endpoint (coinm_futures.account.leverage_bracket_by_symbol) instead."""

  async def leverage_bracket_by_pair(
    self,
    *,
    pair: str | None = None,
    validate: bool | None = None,
  ) -> list[CoinMPairLeverageBracketGroup]:
    """Get a pair's default notional bracket list (v1). Not recommended for continued use: with multiple symbols under one pair carrying different brackets, this can return ambiguous values — prefer the symbol-based v2 endpoint (coinm_futures.account.leverage_bracket_by_symbol) instead.

    Args:
      pair: Trading pair, e.g. BTCUSD. Every pair's brackets are returned when omitted.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#notional-bracket-for-pair)
    """
    params = {}
    if pair is not None:
      params['pair'] = pair
    _Response = list[CoinMPairLeverageBracketGroup]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/dapi/v1/leverageBracket',
      params=params,
      validator=_validator,
      validate=validate,
    )
