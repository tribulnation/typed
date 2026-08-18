from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginSmallLiability(TypedDict):
  """A single liability eligible for small liability exchange."""

  asset: str
  """Borrowed asset eligible for exchange."""
  interest: str
  """Accrued interest on this liability, as a decimal string."""
  principal: str
  """Loan principal on this liability, as a decimal string."""
  liabilityAsset: str
  """Asset the liability would be exchanged into."""
  liabilityQty: str
  """Total liability quantity eligible for exchange, as a decimal string. Corrected from live evidence: the docs-only pass had this typed `number`, but Binance's usual decimal-as-string convention holds here too (`"0.01490522"`)."""


class SmallLiabilityExchangeCoins(RpcEndpoint):
  """Get Small Liability Exchange Coin List"""

  async def small_liability_exchange_coins(
    self,
    *,
    validate: bool | None = None,
  ) -> list[MarginSmallLiability]:
    """Query this margin account's liabilities eligible for small liability exchange (converting small debt balances into a single liability asset).

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-small-liability-exchange-coin-list)
    """
    _Response = list[MarginSmallLiability]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/exchange-small-liability',
      validator=_validator,
      validate=validate,
    )
