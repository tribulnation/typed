from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class CoinNetwork(TypedDict):
  """Network settings."""
  coin: str | None
  """Currency code."""
  depositEnable: bool | None
  """Whether deposits are enabled on this network."""
  withdrawEnable: bool | None
  """Whether withdrawals are enabled on this network."""
  withdrawFee: str | None
  """Withdrawal fee."""
  withdrawMax: str | None
  """Maximum withdrawal amount."""
  withdrawMin: str | None
  """Minimum withdrawal amount."""
  contract: NotRequired[str | None]
  """Token contract address, when applicable."""
  network: str | None
  """Withdrawal network identifier."""
  netWork: str | None
  """New withdrawal network identifier used by newer withdraw endpoint."""
  memo: NotRequired[str | None]
  """Memo/tag requirement, when present."""
  Name: NotRequired[str | None]
  """Legacy network display name returned by older API responses."""
  name: str
  """Network display name returned by the current API."""
  depositDesc: str | None
  """Deposit availability description when deposits are restricted."""
  depositTips: str | None
  """Deposit instructions when applicable."""
  depositPreConfirms: int | None
  """Pre-credit confirmation count when configured for the network."""
  minConfirm: int
  """Returned minConfirm field."""
  sameAddress: bool
  """Returned sameAddress field."""
  withdrawIntegerMultiple: str | None
  """Required withdrawal amount multiple when applicable."""
  withdrawTips: str | None
  """Withdrawal instructions when applicable."""

class CurrencyInfoItem(TypedDict):
  """Currency configuration."""
  coin: str | None
  """Currency code."""
  Name: NotRequired[str | None]
  """Legacy currency display name returned by older API responses."""
  name: str
  """Currency display name returned by the current API."""
  networkList: list[CoinNetwork]
  """Network-specific deposit and withdrawal settings."""

Response: type[list[CurrencyInfoItem] | ErrorResponse] = list[CurrencyInfoItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class CurrencyInfo(AuthSpotMixin):
  async def currency_info(
    self, *,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> list[CurrencyInfoItem]:
    """Returns supported currencies, deposit/withdrawal availability, network limits, fees, and contract metadata for wallet operations.

    Args:
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-the-currency-information)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/config/getall', params=params)
    return self.output(r.text, adapter, validate)
