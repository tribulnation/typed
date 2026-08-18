from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerSubAccountUsdmFuturesCommissionInfo(TypedDict):
  """USDⓈ-M futures commission for one sub-account symbol."""

  subAccountId: int
  """Sub-account identifier."""
  symbol: str
  """USDⓈ-M futures symbol."""
  makerCommission: int
  """Effective maker commission."""
  takerCommission: int
  """Effective taker commission."""


class SubAccountUsdmFuturesCommission(RpcEndpoint):
  """Query Sub Account USDT-Ⓜ Futures Commission Adjustment"""

  async def sub_account_usdm_futures_commission(
    self,
    *,
    sub_account_id: str,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[BrokerSubAccountUsdmFuturesCommissionInfo]:
    """Query a sub-account's USDⓈ-M futures commission rates.

    Args:
      sub_account_id: Sub-account identifier.
      symbol: USDⓈ-M futures symbol. All symbols if omitted.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params: dict = {
      'subAccountId': sub_account_id,
    }
    if symbol is not None:
      params['symbol'] = symbol
    _Response = list[BrokerSubAccountUsdmFuturesCommissionInfo]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/broker/subAccountApi/commission/futures',
      params=params,
      validator=_validator,
      validate=validate,
    )
