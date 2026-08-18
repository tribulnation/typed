from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BlvtSubscriptionRecord(TypedDict):
  """One historical BLVT subscription."""

  id: int
  """Subscription record identifier."""
  tokenName: str
  """Leveraged token name subscribed to."""
  amount: str
  """Token amount subscribed."""
  nav: str
  """NAV price at time of subscription."""
  fee: str
  """Subscription fee, in USDT."""
  totalCharge: str
  """Total subscription cost, in USDT."""
  timestamp: Timestamp
  """Time the subscription was processed."""


class SubscribeRecord(RpcEndpoint):
  """Query Subscription Record (USER_DATA)"""

  async def subscribe_record(
    self,
    *,
    token_name: str | None = None,
    id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[BlvtSubscriptionRecord]:
    """Get historical BLVT subscription records. Only the latest 90 days of data is available.

    Args:
      token_name: Leveraged token name, e.g. `BTCDOWN`, `BTCUP`.
      id: Subscription record identifier to filter by.
      start_time: Start of the query window, UTC ms.
      end_time: End of the query window, UTC ms.
      limit: Maximum records to return. Default 500, max 1000.

    References:
      - [Official docs](https://github.com/binance/binance-api-swagger)
    """
    params = {}
    if token_name is not None:
      params['tokenName'] = token_name
    if id is not None:
      params['id'] = id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[BlvtSubscriptionRecord]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/blvt/subscribe/record',
      params=params,
      validator=_validator,
      validate=validate,
    )
