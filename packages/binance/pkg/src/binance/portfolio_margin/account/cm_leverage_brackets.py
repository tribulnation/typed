from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmCmNotionalAndLeverageBrackets(TypedDict):
  """PmCmNotionalAndLeverageBrackets."""

  symbol: NotRequired[str]
  """Trade symbol, if existing."""


class CmLeverageBrackets(RpcEndpoint):
  """CM Notional and Leverage Brackets"""

  async def cm_leverage_brackets(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[PmCmNotionalAndLeverageBrackets]:
    """Query CM notional and leverage brackets.

    Args:
      symbol: Trading pair symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#cm-notional-and-leverage-brackets)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = list[PmCmNotionalAndLeverageBrackets]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/cm/leverageBracket',
      params=params,
      validator=_validator,
      validate=validate,
    )
