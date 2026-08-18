from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerSubAccountCoinmFuturesAsset(TypedDict):
  """One sub-account's summary."""

  futuresEnable: bool
  """Whether futures is enabled for this sub-account."""
  subAccountId: str
  """Sub-account identifier."""
  totalWalletBalanceOfUsdt: NotRequired[str]
  """Total futures wallet balance, valued in USDT."""
  totalUnrealizedProfitOfUsdt: NotRequired[str]
  """Total unrealized PnL, valued in USDT."""
  totalMarginBalanceOfUsdt: NotRequired[str]
  """Total margin balance, valued in USDT."""


class BrokerSubAccountUsdmFuturesAsset(TypedDict):
  """One sub-account's summary."""

  futuresEnable: bool
  """Whether futures is enabled for this sub-account."""
  subAccountId: str
  """Sub-account identifier."""
  totalInitialMarginOfUsdt: NotRequired[str]
  """Total initial margin required, in USDT."""
  totalMaintenanceMarginOfUsdt: NotRequired[str]
  """Total maintenance margin required, in USDT."""
  totalWalletBalanceOfUsdt: NotRequired[str]
  """Total futures wallet balance, in USDT."""
  totalUnrealizedProfitOfUsdt: NotRequired[str]
  """Total unrealized PnL, in USDT."""
  totalMarginBalanceOfUsdt: NotRequired[str]
  """Total margin balance, in USDT."""
  totalPositionInitialMarginOfUsdt: NotRequired[str]
  """Initial margin held by open positions, in USDT."""
  totalOpenOrderInitialMarginOfUsdt: NotRequired[str]
  """Initial margin held by open orders, in USDT."""


class BrokerSubAccountFuturesSummaryV2coinm(TypedDict):
  """Page of per-sub-account summaries. `futuresType=2` (COIN-M) shape."""

  data: list[BrokerSubAccountCoinmFuturesAsset]
  """Per-sub-account summaries."""
  timestamp: Timestamp
  """Time this snapshot was computed."""


class BrokerSubAccountFuturesSummaryV2usdm(TypedDict):
  """Page of per-sub-account summaries. `futuresType=1` (USDⓈ-M) shape."""

  data: list[BrokerSubAccountUsdmFuturesAsset]
  """Per-sub-account summaries."""
  timestamp: Timestamp
  """Time this snapshot was computed."""


class SubAccountFuturesSummaryV2(RpcEndpoint):
  """Query Subaccount Futures Asset info (V2)"""

  async def sub_account_futures_summary_v2(
    self,
    *,
    sub_account_id: str | None = None,
    futures_type: Literal[1, 2],
    page: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> BrokerSubAccountFuturesSummaryV2usdm | BrokerSubAccountFuturesSummaryV2coinm:
    """Get futures asset totals across sub-accounts for one futures product. `futuresType`: `1` = USDⓈ-M Futures, `2` = COIN-M Futures — the response shape differs by which was requested.

    Args:
      sub_account_id: Sub-account identifier. All sub-accounts if omitted.
      futures_type: Futures product to summarize.
      page: Page number, 1-indexed. Default 1.
      size: Records per page. Default 10, max 20.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params: dict = {
      'futuresType': futures_type,
    }
    if sub_account_id is not None:
      params['subAccountId'] = sub_account_id
    if page is not None:
      params['page'] = page
    if size is not None:
      params['size'] = size
    _Response = (
      BrokerSubAccountFuturesSummaryV2usdm | BrokerSubAccountFuturesSummaryV2coinm
    )
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'GET',
      '/sapi/v2/broker/subAccount/futuresSummary',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def sub_account_futures_summary_v2_paged(
    self,
    *,
    sub_account_id: str | None = None,
    futures_type: Literal[1, 2],
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[
    BrokerSubAccountFuturesSummaryV2usdm | BrokerSubAccountFuturesSummaryV2coinm
  ]:
    """Yield successive pages of `sub_account_futures_summary_v2`.

    Requests `page` from 1 upwards and stops on the first page shorter than `size`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.sub_account_futures_summary_v2(
        sub_account_id=sub_account_id,
        futures_type=futures_type,
        size=size,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('data') if response is not None else None
      if not rows or (size is not None and len(rows) < size):
        break
      page += 1
