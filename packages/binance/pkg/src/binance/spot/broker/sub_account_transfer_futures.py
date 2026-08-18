from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerFuturesTransfer(TypedDict):
  """Result of a futures transfer between broker/master and a sub-account."""

  success: bool
  """Whether the transfer succeeded."""
  txnId: str
  """Transfer transaction identifier."""
  clientTranId: str
  """Caller-supplied idempotency id echoed back, if any."""


class SubAccountTransferFutures(RpcEndpoint):
  """Sub Account Transfer (FUTURES)"""

  async def sub_account_transfer_futures(
    self,
    *,
    from_id: str | None = None,
    to_id: str | None = None,
    futures_type: Literal[1, 2],
    asset: str,
    amount: float,
    client_tran_id: str | None = None,
    validate: bool | None = None,
  ) -> BrokerFuturesTransfer:
    """Transfer an asset between the master account and a sub-account's futures wallet, or between two sub-accounts. `futuresType`: `1` = USDⓈ-M Futures, `2` = COIN-M Futures.

    Args:
      from_id: Source sub-account. Transfers from the master account if omitted.
      to_id: Destination sub-account. Transfers to the master account if omitted.
      futures_type: Futures product to transfer within.
      asset: Asset to transfer.
      amount: Amount to transfer.
      client_tran_id: Caller-supplied idempotency id. Max 32 characters.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params: dict = {
      'futuresType': futures_type,
      'asset': asset,
      'amount': amount,
    }
    if from_id is not None:
      params['fromId'] = from_id
    if to_id is not None:
      params['toId'] = to_id
    if client_tran_id is not None:
      params['clientTranId'] = client_tran_id
    _Response = BrokerFuturesTransfer
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/broker/transfer/futures',
      params=params,
      validator=_validator,
      validate=validate,
    )
