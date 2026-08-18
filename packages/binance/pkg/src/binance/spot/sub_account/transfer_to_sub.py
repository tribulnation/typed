from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class TransferToSubAccountResult(TypedDict):
  """The executed transfer."""

  txnId: NotRequired[str]
  """Transaction id of the transfer."""


class TransferToSub(RpcEndpoint):
  """Transfer an asset from the calling sub-account to another sub-account of the same master."""

  async def __call__(
    self,
    *,
    to_email: str,
    asset: str,
    amount: float,
    validate: bool | None = None,
  ) -> TransferToSubAccountResult:
    """Transfer an asset from the calling sub-account to another sub-account of the same master.

    Args:
      to_email: Email of the receiving sub-account.
      asset: Asset to transfer.
      amount: Amount to transfer.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#transfer-to-sub-account-of-same-master)
    """
    params: dict = {
      'toEmail': to_email,
      'asset': asset,
      'amount': amount,
    }
    _Response = TransferToSubAccountResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/sub-account/transfer/subToSub',
      params=params,
      validator=_validator,
      validate=validate,
    )
