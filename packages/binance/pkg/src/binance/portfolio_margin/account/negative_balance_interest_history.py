from typing_extensions import Any
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class NegativeBalanceInterestHistory(RpcEndpoint):
  """Query Portfolio Margin Negative Balance Interest History"""

  async def negative_balance_interest_history(
    self,
    *,
    asset: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Query interest history of negative balance for portfolio margin.

    Args:
      asset: Asset name.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      size: Number of results returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-portfolio-margin-negative-balance-interest-history)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if size is not None:
      params['size'] = size
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/portfolio/interest-history',
      params=params,
      validator=_validator,
      validate=validate,
    )
