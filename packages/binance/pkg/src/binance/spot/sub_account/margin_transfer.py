from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginTransferResult(TypedDict):
  """The executed transfer."""

  txnId: NotRequired[str]
  """Transaction id of the transfer."""


class MarginTransfer(RpcEndpoint):
  """Transfer an asset between a sub-account's Spot and Margin wallets, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    asset: str,
    amount: float,
    type: Literal[1, 2],
    validate: bool | None = None,
  ) -> MarginTransferResult:
    """Transfer an asset between a sub-account's Spot and Margin wallets, for the master account.

    Args:
      email: Sub-account email.
      asset: Asset to transfer.
      amount: Amount to transfer.
      type: Transfer direction: `1` = spot to margin, `2` = margin to spot.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#margin-transfer-for-sub-account)
    """
    params: dict = {
      'email': email,
      'asset': asset,
      'amount': amount,
      'type': type,
    }
    _Response = MarginTransferResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/sub-account/margin/transfer',
      params=params,
      validator=_validator,
      validate=validate,
    )
