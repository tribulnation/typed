from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SymbolCommissionFee(TypedDict):
  """Maker/taker commission fee rate for one account and symbol."""

  userId: NotRequired[int]
  """Account user ID this commission fee applies to."""
  symbol: NotRequired[str]
  """Trading pair symbol."""
  makerCommission: NotRequired[str]
  """Maker commission fee rate, excluding any Spot market maker rebate or BNB discount."""
  takerCommission: NotRequired[str]
  """Taker commission fee rate, excluding any BNB discount."""


class CommissionFee(RpcEndpoint):
  """Query the maker/taker commission fee rate for a symbol. A master account can query the rate for a specific symbol of one of its sub-accounts. Not supported for broker accounts. Excludes the Spot market maker rebate rate and any BNB fee discount."""

  async def commission_fee(
    self,
    *,
    user_id: int | None = None,
    symbol: str,
    validate: bool | None = None,
  ) -> SymbolCommissionFee:
    """Query the maker/taker commission fee rate for a symbol. A master account can query the rate for a specific symbol of one of its sub-accounts. Not supported for broker accounts. Excludes the Spot market maker rebate rate and any BNB fee discount.

    Args:
      user_id: Sub-account user ID to query the commission fee for. Only usable by a master account querying one of its sub-accounts; omit to query the calling account itself.
      symbol: Trading pair symbol to query the commission fee for.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-vip-service/api/rest-api/~#query-symbol-commission-fee)
    """
    params: dict = {
      'symbol': symbol,
    }
    if user_id is not None:
      params['userId'] = user_id
    _Response = SymbolCommissionFee
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/commission/queryCommissionFee',
      params=params,
      validator=_validator,
      validate=validate,
    )
