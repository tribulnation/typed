from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class UniversalTransferByTranIdResponse(TypedDict):
  """Universal transfer detail."""
  tranId: str | None
  """Transfer id."""
  clientTranId: str | None
  """Client transfer id."""
  asset: str | None
  """Asset."""
  amount: str | None
  """Amount."""
  fromAccountType: str | None
  """Source account type."""
  toAccountType: str | None
  """Destination account type."""
  symbol: str | None
  """Symbol."""
  status: str | None
  """Transfer status."""
  timestamp: Timestamp | None
  """Transfer timestamp."""

Response: type[UniversalTransferByTranIdResponse | ErrorResponse] = UniversalTransferByTranIdResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class UniversalTransferByTranId(AuthSpotMixin):
  async def universal_transfer_by_tran_id(
    self, *,
    tran_id: str, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> UniversalTransferByTranIdResponse:
    """Returns a single universal transfer record by transfer id.

    Args:
      tran_id: Transfer id.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history-by-tranid)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if tran_id is not None:
      params['tranId'] = tran_id
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/transfer/tranId', params=params)
    return self.output(r.text, adapter, validate)
