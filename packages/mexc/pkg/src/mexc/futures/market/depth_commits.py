from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import FuturesMixin

class DepthCommitsItem(TypedDict):
  """Depth snapshot or incremental depth commit."""
  asks: list[tuple[float, float, int]]
  """Ask-side depth levels."""
  bids: list[tuple[float, float, int]]
  """Bid-side depth levels."""
  version: int
  """Depth version number."""
  timestamp: NotRequired[Timestamp]
  """System timestamp in milliseconds."""

class DepthCommitsResponse(TypedDict):
  """Depth commits envelope"""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[DepthCommitsItem]]
  """Latest depth commit records."""

adapter = validator(DepthCommitsResponse)

class DepthCommits(FuturesMixin):
  async def depth_commits(
    self, symbol: str, limit: int, *,
    validate: bool | None = None,
  ) -> DepthCommitsResponse:
    """Return the latest N depth snapshots/commits for a contract.

    Args:
      symbol: Contract symbol, for example BTC_USDT.
      limit: Number of latest depth commits to return.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-a-snapshot-of-the-latest-n-depth-information-of-the-contract)
    """
    params = {}
    r = await self.request('GET', '/api/v1/contract/depth_commits/{symbol}/{limit}'.replace('{symbol}', str(symbol)).replace('{limit}', str(limit)))
    return self.envelope_output(r.text, adapter, validate)
