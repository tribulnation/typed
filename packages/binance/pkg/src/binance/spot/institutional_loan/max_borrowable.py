from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MaxBorrowable(TypedDict):
  """Maximum borrowable amount."""

  maxBorrowableAmount: NotRequired[str]
  """Max borrowable amount of the asset for the risk unit. Empty/null when the caller has no matching risk unit."""


class MaxBorrowableEndpoint(RpcEndpoint):
  """Query the maximum borrowable amount of a given asset for an institutional loan risk unit. Callable with either the parent or the credit account API key. For the credit account, `groupId` is optional -- omitted defaults to the member's own risk unit, provided it must match that risk unit or an empty result is returned. For the parent account, `groupId` is required and must be owned by that parent account, or an empty result is returned. A caller that is neither the parent account nor a credit member of the group (e.g. a collateral member, or no matching risk unit) gets an empty/null `maxBorrowableAmount`."""

  async def max_borrowable(
    self,
    *,
    group_id: int | None = None,
    asset_name: str,
    validate: bool | None = None,
  ) -> MaxBorrowable:
    """Query the maximum borrowable amount of a given asset for an institutional loan risk unit. Callable with either the parent or the credit account API key. For the credit account, `groupId` is optional -- omitted defaults to the member's own risk unit, provided it must match that risk unit or an empty result is returned. For the parent account, `groupId` is required and must be owned by that parent account, or an empty result is returned. A caller that is neither the parent account nor a credit member of the group (e.g. a collateral member, or no matching risk unit) gets an empty/null `maxBorrowableAmount`.

    Args:
      group_id: Risk unit unique identifier. Optional when the API key belongs to the credit member; required when it belongs to the parent account.
      asset_name: Asset to borrow. Case-insensitive (normalized to upper-case). Must be a borrowable asset, otherwise an error is returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-institutional-loan/api/rest-api/borrow-repay#query-loan-group-max-borrowable)
    """
    params: dict = {
      'assetName': asset_name,
    }
    if group_id is not None:
      params['groupId'] = group_id
    _Response = MaxBorrowable
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/loan-group/max-borrowable',
      params=params,
      validator=_validator,
      validate=validate,
    )
