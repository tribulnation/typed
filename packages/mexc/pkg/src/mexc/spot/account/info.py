from typing_extensions import Literal, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class SpotBalance(TypedDict):
  """Balance."""
  asset: str
  """Asset the balance is held in."""
  free: str
  """Amount available to trade or withdraw."""
  locked: str
  """Amount reserved by open orders."""

class SpotAccountInfo(TypedDict):
  """Account information response."""
  canTrade: bool
  """Whether spot trading is enabled."""
  canWithdraw: bool
  """Whether withdrawals are enabled."""
  canDeposit: bool
  """Whether deposits are enabled."""
  updateTime: Timestamp | None
  """Account update time."""
  accountType: Literal['SPOT']
  """Account type; the spot account endpoint only ever reports `SPOT`."""
  balances: list[SpotBalance]
  """Asset balances."""
  permissions: list[str]
  """Account permissions."""

Response: type[SpotAccountInfo | ErrorResponse] = SpotAccountInfo | ErrorResponse # type: ignore
adapter = validator(Response)

class Info(AuthSpotMixin):
  async def info(
    self, *,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> SpotAccountInfo:
    """Returns trading permissions and spot balances for the signed account.

    Args:
      recv_window: Optional receive window in milliseconds; maximum 60000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#account-information)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/account', params=params)
    return self.output(r.text, adapter, validate)
