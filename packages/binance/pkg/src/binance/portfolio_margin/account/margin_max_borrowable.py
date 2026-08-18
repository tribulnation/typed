from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmMarginMaxBorrow(TypedDict):
  """Query margin max borrow."""

  amount: NotRequired[str]
  """account's currently max borrowable amount with sufficient system availability."""
  borrowLimit: NotRequired[str]
  """max borrowable amount limited by the account level."""


class MarginMaxBorrowable(RpcEndpoint):
  """Margin Max Borrow"""

  async def margin_max_borrowable(
    self,
    *,
    asset: str,
    validate: bool | None = None,
  ) -> PmMarginMaxBorrow:
    """Query margin max borrow.

    Args:
      asset: Asset name.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#margin-max-borrow)
    """
    params: dict = {
      'asset': asset,
    }
    _Response = PmMarginMaxBorrow
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/margin/maxBorrowable',
      params=params,
      validator=_validator,
      validate=validate,
    )
