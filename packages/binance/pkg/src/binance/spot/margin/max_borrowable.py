from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginMaxBorrowable(TypedDict):
  """Max borrowable amount details for one asset."""

  amount: str
  """Account's current max borrowable amount with sufficient system availability."""
  borrowLimit: str
  """Max borrowable amount limited by the account level (see https://www.binance.com/en/margin-fee)."""


class MaxBorrowable(RpcEndpoint):
  """Query max borrow"""

  async def max_borrowable(
    self,
    *,
    asset: str,
    isolated_symbol: str | None = None,
    validate: bool | None = None,
  ) -> MarginMaxBorrowable:
    """Query the maximum amount of an asset this account can currently borrow, crossed or for a specific isolated symbol. If `isolatedSymbol` is not sent, crossed margin data is returned. `borrowLimit` is also available at https://www.binance.com/en/margin-fee.

    Args:
      asset: Asset to query.
      isolated_symbol: Isolated margin symbol. If not sent, crossed margin data is returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/borrow-repay#query-max-borrow)
    """
    params: dict = {
      'asset': asset,
    }
    if isolated_symbol is not None:
      params['isolatedSymbol'] = isolated_symbol
    _Response = MarginMaxBorrowable
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/maxBorrowable',
      params=params,
      validator=_validator,
      validate=validate,
    )
