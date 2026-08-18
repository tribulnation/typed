from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerSubAccountCoinmFuturesCommission(TypedDict):
  """Updated COIN-M futures commission for a sub-account pair."""

  subAccountId: int
  """Sub-account identifier."""
  pair: str
  """COIN-M futures pair."""
  makerAdjustment: int
  """New maker commission adjustment."""
  takerAdjustment: int
  """New taker commission adjustment."""
  makerCommission: int
  """Resulting effective maker commission."""
  takerCommission: int
  """Resulting effective taker commission."""


class ChangeSubAccountCoinmFuturesCommission(RpcEndpoint):
  """Change Sub Account COIN-Ⓜ Futures Commission Adjustment"""

  async def change_sub_account_coinm_futures_commission(
    self,
    *,
    sub_account_id: str,
    pair: str,
    maker_adjustment: int,
    taker_adjustment: int,
    validate: bool | None = None,
  ) -> BrokerSubAccountCoinmFuturesCommission:
    """Adjust a sub-account's COIN-M futures commission rate for one pair.

    Args:
      sub_account_id: Sub-account identifier.
      pair: COIN-M futures pair, e.g. `BTCUSD`.
      maker_adjustment: Maker commission adjustment; `100` means 0.01%.
      taker_adjustment: Taker commission adjustment; `100` means 0.01%.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params: dict = {
      'subAccountId': sub_account_id,
      'pair': pair,
      'makerAdjustment': maker_adjustment,
      'takerAdjustment': taker_adjustment,
    }
    _Response = BrokerSubAccountCoinmFuturesCommission
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/broker/subAccountApi/commission/coinFutures',
      params=params,
      validator=_validator,
      validate=validate,
    )
