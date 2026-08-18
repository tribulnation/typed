from typing_extensions import Literal, NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import AuthFuturesMixin

class OpenPosition(TypedDict):
  """Futures position record."""
  positionId: int | str
  """Position identifier."""
  symbol: str
  """Contract symbol."""
  positionType: Literal[1, 2]
  """Position side: 1 long, 2 short."""
  openType: Literal[1, 2]
  """Margin mode: 1 isolated, 2 cross."""
  state: Literal[1, 2, 3]
  """Position state: 1 holding, 2 system auto-holding, 3 closed."""
  holdVol: float
  """Held contract volume."""
  frozenVol: float
  """Frozen position volume."""
  closeVol: float
  """Closed position volume."""
  holdAvgPrice: float
  """Average holding price."""
  openAvgPrice: float
  """Average opening price."""
  closeAvgPrice: float
  """Average closing price."""
  liquidatePrice: float
  """Liquidation price."""
  oim: float
  """Original initial margin."""
  im: float
  """Initial margin."""
  holdFee: float
  """Holding fee."""
  realised: float
  """Realized profit and loss."""
  adlLevel: NotRequired[int]
  """Current ADL level when present."""
  leverage: int
  """Position leverage."""
  createTime: Timestamp | Timestamp
  """Creation time."""
  updateTime: Timestamp | Timestamp
  """Last update time."""
  autoAddIm: bool
  """Whether automatic margin addition is enabled."""

class OpenPositionsResponse(TypedDict):
  """Get open futures positions response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[OpenPosition]]
  """Current open futures positions."""

adapter = validator(OpenPositionsResponse)

class Open(AuthFuturesMixin):
  async def open(
    self, *,
    symbol: str | None = None, validate: bool | None = None,
  ) -> OpenPositionsResponse:
    """Returns current open holding positions for the signed futures account.

    Args:
      symbol: Optional contract symbol; omitted returns all open positions.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-39-s-current-holding-position)
    """
    headers = {}
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.signed_request('GET', '/api/v1/private/position/open_positions', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)
