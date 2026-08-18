from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AssetDetail(TypedDict):
  """Deposit/withdraw detail for a single asset."""

  minWithdrawAmount: str
  """Minimum withdrawal amount."""
  depositStatus: bool
  """Whether deposits are enabled for this asset (false if disabled on every network)."""
  withdrawFee: str
  """Withdrawal fee, as a decimal string."""
  withdrawStatus: bool
  """Whether withdrawals are enabled for this asset (false if disabled on every network)."""
  depositTip: NotRequired[str]
  """Human-readable note about a deposit/withdraw restriction on this asset. Present only when a restriction applies."""


class Detail(RpcEndpoint):
  """Fetch deposit/withdraw details of assets supported on Binance. Network-level deposit/withdraw configuration lives on `spot.wallet.capital.config.get_all` instead."""

  async def __call__(
    self,
    *,
    asset: str | None = None,
    validate: bool | None = None,
  ) -> dict[str, AssetDetail]:
    """Fetch deposit/withdraw details of assets supported on Binance. Network-level deposit/withdraw configuration lives on `spot.wallet.capital.config.get_all` instead.

    Args:
      asset: Asset to query. Returns every asset when omitted.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#asset-detail)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    _Response = dict[str, AssetDetail]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/asset/assetDetail',
      params=params,
      validator=_validator,
      validate=validate,
    )
