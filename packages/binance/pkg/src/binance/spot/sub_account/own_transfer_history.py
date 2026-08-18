from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountOwnTransfer(TypedDict):
  """One transfer into or out of the calling sub-account."""

  counterParty: NotRequired[str]
  """The other party to the transfer (`master` or the counterpart sub-account's identifier)."""
  email: NotRequired[str]
  """Email of the counterparty account."""
  type: NotRequired[Literal[1, 2]]
  """Transfer direction: `1` = transfer in, `2` = transfer out."""
  asset: NotRequired[str]
  """Asset transferred."""
  qty: NotRequired[str]
  """Amount transferred."""
  fromAccountType: NotRequired[str]
  """Account type transferred from."""
  toAccountType: NotRequired[str]
  """Account type transferred to."""
  status: NotRequired[str]
  """Transfer status."""
  tranId: NotRequired[int]
  """Transfer id."""
  time: NotRequired[int]
  """Time the transfer was executed."""


class OwnTransferHistory(RpcEndpoint):
  """Query the calling sub-account's own transfer history."""

  async def __call__(
    self,
    *,
    asset: str | None = None,
    type: Literal[1, 2] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    return_fail_history: bool | None = None,
    validate: bool | None = None,
  ) -> list[SubAccountOwnTransfer]:
    """Query the calling sub-account's own transfer history.

    Args:
      asset: Filter by asset. Omit to return every asset.
      type: Transfer direction: `1` = transfer in, `2` = transfer out.
      start_time: Start of the query window.
      end_time: End of the query window.
      limit: Page size. The upstream docs state a default of 500 and a maximum of 200 for this parameter, which is internally contradictory; left unresolved pending a live call (spec-authoring rule 7).
      return_fail_history: Whether to also return `FAILURE`-status records, in addition to `PROCESS` and `SUCCESS`. Defaults to `false`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#sub-account-transfer-history)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if type is not None:
      params['type'] = type
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    if return_fail_history is not None:
      params['returnFailHistory'] = return_fail_history
    _Response = list[SubAccountOwnTransfer]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/transfer/subUserHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )
