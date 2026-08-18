from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FundNavEntry(TypedDict):
  """One day's NAV entry for the fund."""

  date: NotRequired[str]
  """Date this NAV entry applies to, formatted `YYYYMMDD`."""
  nav: NotRequired[int]
  """Total Net Asset Value on this date, in `fundCurrency`."""
  unit: NotRequired[int]
  """Total outstanding units on this date."""
  navPerUnit: NotRequired[float]
  """Net Asset Value per unit on this date."""


class FundNavHistory(TypedDict):
  """A fund's identity and its last 30-day NAV history."""

  fundAccountId: NotRequired[int]
  """Fund account ID."""
  fundName: NotRequired[str]
  """Fund name."""
  fundNavs: NotRequired[list[FundNavEntry]]
  """Daily NAV entries over the last 30 days."""


class FundNavHistoryEndpoint(RpcEndpoint):
  """Query the last 30-day Net-Asset-Value (NAV) history for a fund under a fund manager master account."""

  async def fund_nav_history(
    self,
    *,
    fund_account_id: int,
    validate: bool | None = None,
  ) -> FundNavHistory:
    """Query the last 30-day Net-Asset-Value (NAV) history for a fund under a fund manager master account.

    Args:
      fund_account_id: Fund Account ID.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-fund-account/api/rest-api/~#query-fund-nav-history)
    """
    params: dict = {
      'fundAccountId': fund_account_id,
    }
    _Response = FundNavHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/vip/fund-info/fund-nav-info',
      params=params,
      validator=_validator,
      validate=validate,
    )
