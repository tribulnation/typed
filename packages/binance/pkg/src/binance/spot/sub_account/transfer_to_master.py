from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class TransferToMasterResult(TypedDict):
  """The executed transfer."""

  txnId: NotRequired[str]
  """Transaction id of the transfer."""


class TransferToMaster(RpcEndpoint):
  """Transfer an asset from the calling sub-account to the master account."""

  async def __call__(
    self,
    *,
    asset: str,
    amount: float,
    validate: bool | None = None,
  ) -> TransferToMasterResult:
    """Transfer an asset from the calling sub-account to the master account.

    Args:
      asset: Asset to transfer.
      amount: Amount to transfer.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#transfer-to-master)
    """
    params: dict = {
      'asset': asset,
      'amount': amount,
    }
    _Response = TransferToMasterResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/sub-account/transfer/subToMaster',
      params=params,
      validator=_validator,
      validate=validate,
    )
