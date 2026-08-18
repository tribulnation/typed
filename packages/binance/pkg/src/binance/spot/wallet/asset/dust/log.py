from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DustDribbletDetail(TypedDict):
  """Conversion detail for a single source asset within one exchange."""

  transId: int
  """Transaction ID for this asset's leg of the exchange."""
  serviceChargeAmount: str
  """BNB service charge for this asset."""
  amount: str
  """Amount of the source asset converted."""
  operateTime: int
  """Conversion time, as milliseconds since epoch."""
  transferedAmount: str
  """BNB amount credited for this asset."""
  fromAsset: str
  """Source asset converted."""


class DustDribbletExchange(TypedDict):
  """One dust-conversion exchange, covering one or more source assets converted at the same time."""

  operateTime: int
  """Exchange time, as milliseconds since epoch."""
  totalTransferedAmount: str
  """Total BNB amount credited across this exchange."""
  totalServiceChargeAmount: str
  """Total BNB service charge across this exchange."""
  transId: int
  """Transaction ID for this exchange."""
  userAssetDribbletDetails: list[DustDribbletDetail]
  """Per-source-asset breakdown of this exchange."""


class DustLog(TypedDict):
  """Historical dust-to-BNB conversion log."""

  total: int
  """Total number of dust-conversion exchanges (batches) returned."""
  userAssetDribblets: list[DustDribbletExchange]
  """One entry per dust-conversion exchange (a batch of assets converted together)."""


class Log(RpcEndpoint):
  """Fetch historical dust-to-BNB conversion records ("DustLog"). Only returns the last 100 records, and only records after 2020-12-01."""

  async def log(
    self,
    *,
    account_type: Literal['SPOT', 'MARGIN'] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    validate: bool | None = None,
  ) -> DustLog:
    """Fetch historical dust-to-BNB conversion records ("DustLog"). Only returns the last 100 records, and only records after 2020-12-01.

    Args:
      account_type: Wallet the dust was converted from.
      start_time: Query period start, as milliseconds since epoch.
      end_time: Query period end, as milliseconds since epoch.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dustlog)
    """
    params = {}
    if account_type is not None:
      params['accountType'] = account_type
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    _Response = DustLog
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/asset/dribblet',
      params=params,
      validator=_validator,
      validate=validate,
    )
