from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class HistoryItem(TypedDict):
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
  createTime: int | str
  """Creation time."""
  updateTime: int | str
  """Last update time."""
  autoAddIm: bool
  """Whether automatic margin addition is enabled."""

class HistoryResponse(TypedDict):
  """Get historical futures positions response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[HistoryItem]]
  """Historical futures positions."""

adapter = validator(HistoryResponse)

class History(AuthFuturesMixin):
  async def history(
    self, *,
    symbol: str | None = None, type_: Literal[1, 2] | None = None, page_num: int,
    page_size: int, validate: bool | None = None,
  ) -> HistoryResponse:
    """Returns paginated historical position records for the signed futures account.

    Args:
      symbol: Contract symbol filter.
      type_: Position type filter: 1 long, 2 short.
      page_num: Page number; default is 1.
      page_size: Page size; default 20, maximum 100.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-s-history-position-information)
    """
    headers = {}
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if type_ is not None:
      params['type'] = type_
    if page_num is not None:
      params['page_num'] = page_num
    if page_size is not None:
      params['page_size'] = page_size
    r = await self.signed_request('GET', '/api/v1/private/position/list/history_positions', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)

  async def history_paged(
    self, *,
    symbol: str | None = None, type_: Literal[1, 2] | None = None, page_size: int,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[HistoryResponse]:
    """Yield successive pages of `history`.

    Requests `page_num` from 1 upwards and stops on the first page shorter than
    `page_size`, or after `max_pages` pages when one is given.
    """
    page_num = 1
    pages = 0
    while True:
      response = await self.history(symbol=symbol, type_=type_, page_size=page_size, page_num=page_num, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('data') if response is not None else None
      if not rows or len(rows) < page_size:
        break
      page_num += 1
