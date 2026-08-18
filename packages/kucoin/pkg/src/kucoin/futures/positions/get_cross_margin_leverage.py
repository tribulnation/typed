"""`GET /api/v2/getCrossUserLeverage` — Get Cross Margin Leverage."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CrossMarginLeverage(TypedDict):
  """Cross-margin leverage currently set for a symbol."""

  symbol: str
  """Symbol of the contract."""
  leverage: str
  """Leverage multiple."""


_Type = CrossMarginLeverage
adapter = validator[_Type](_Type)  # type: ignore


class GetCrossMarginLeverage(RpcEndpoint):
  """`Get Cross Margin Leverage` — mixed into `Positions`, the product exposing `futures.positions.get_cross_margin_leverage`."""

  async def get_cross_margin_leverage(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> CrossMarginLeverage:
    """Query the current cross-margin leverage multiple set for a symbol.

    Args:
      symbol: Symbol of the contract, e.g. `XBTUSDTM`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'GET',
      '/api/v2/getCrossUserLeverage',
      params=params,
      validator=adapter,
      validate=validate,
    )
