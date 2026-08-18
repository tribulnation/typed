"""`spot.account.trades_history` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class HistoricalTrade(TypedDict):
  """One historical trade."""

  ordertxid: NotRequired[str]
  """Order responsible for execution of the trade."""
  postxid: NotRequired[str]
  """Position responsible for execution of the trade."""
  pair: NotRequired[str]
  """Asset pair."""
  time: NotRequired[float]
  """Unix timestamp of the trade."""
  type: NotRequired[Literal['buy', 'sell']]
  """Type of order."""
  ordertype: NotRequired[str]
  """Order type."""
  price: NotRequired[str]
  """Average price the order was executed at (quote currency)."""
  cost: NotRequired[str]
  """Total cost of the order (quote currency)."""
  fee: NotRequired[str]
  """Total fee (quote currency)."""
  vol: NotRequired[str]
  """Volume (base currency)."""
  margin: NotRequired[str]
  """Initial margin (quote currency)."""
  leverage: NotRequired[str]
  """Amount of leverage used in the trade."""
  misc: NotRequired[str]
  """Comma-delimited list of miscellaneous info: `closing` -- trade closes all or part of a position."""
  ledgers: NotRequired[list[str]]
  """List of ledger ids for entries associated with the trade (if requested)."""
  trade_id: NotRequired[int]
  """Unique identifier of the trade executed."""
  maker: NotRequired[bool]
  """`true` if the trade was executed with the user as the maker, `false` if taker."""
  aclass: NotRequired[str]
  """Asset class of the traded pair."""
  tradeordertype: NotRequired[str]
  """Order type of the trade (e.g. `market`, `limit`). May differ from `ordertype` when the order type was converted on execution."""
  posstatus: NotRequired[Literal['open', 'closed']]
  """Position status. Only present if the trade opened a position."""
  cprice: NotRequired[float]
  """Average price of the closed portion of the position (quote currency). Only present if the trade opened a position."""
  ccost: NotRequired[float]
  """Total cost of the closed portion of the position (quote currency). Only present if the trade opened a position."""
  cfee: NotRequired[float]
  """Total fee of the closed portion of the position (quote currency). Only present if the trade opened a position."""
  cvol: NotRequired[float]
  """Total volume of the closed portion of the position (quote currency). Only present if the trade opened a position."""
  cmargin: NotRequired[float]
  """Total margin freed in the closed portion of the position (quote currency). Only present if the trade opened a position."""
  net: NotRequired[float]
  """Net profit/loss of the closed portion of the position (quote currency). Only present if the trade opened a position."""
  trades: NotRequired[list[str]]
  """List of closing trades for the position (if available). Only present if the trade opened a position."""


class TradeHistory(TypedDict):
  """Trade/fill history."""

  count: NotRequired[int]
  """Amount of available trades matching criteria. Omitted from the response when `without_count` is `true`."""
  trades: NotRequired[dict[str, HistoricalTrade]]
  """Trades, keyed by transaction ID."""


validate_trades_history = validator(TradeHistory)


class TradesHistory(RpcEndpoint):
  """`spot.account.trades_history`."""

  async def trades_history(
    self,
    *,
    type: Literal[
      'all', 'any position', 'closed position', 'closing position', 'no position'
    ]
    | None = None,
    trades: bool | None = None,
    start: int | None = None,
    end: int | None = None,
    ofs: int | None = None,
    without_count: bool | None = None,
    consolidate_taker: bool | None = None,
    ledgers: bool | None = None,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
    aclass: Literal[
      'forex', 'equity_pair', 'futures_contract', 'synthetic_pair', 'external_pair'
    ]
    | None = None,
    pair: str | None = None,
    limit: int | None = None,
  ) -> TradeHistory:
    """Retrieve information about trades/fills. By default, the most recent trades are returned. Unless otherwise stated, costs, fees, prices, and volumes are specified with the precision for the asset pair (`pair_decimals` and `lot_decimals`), not the individual assets' precision (`decimals`).

    **API Key Permissions Required:** `Orders and trades - Query closed orders & trades`

    Args:
      type: Type of trade.
      trades: Whether or not to include trades related to position in output.
      start: Starting unix timestamp or trade tx ID of results (exclusive).
      end: Ending unix timestamp or trade tx ID of results (inclusive).
      ofs: Result offset for pagination.
      without_count: If true, does not retrieve the count of matching trades. Request can be noticeably faster for users with many trades, as this avoids an extra database query.
      consolidate_taker: Whether or not to consolidate trades by individual taker trades.
      ledgers: Whether or not to include related ledger ids for a given trade. Setting this to true will slow request performance.
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.
      aclass: Asset class of the `pair` filter.
      pair: Filter results to a single trading pair. An unrecognized pair returns `EQuery:Unknown asset pair`.
      limit: Number of trades returned per page. Values above 100 get clamped to 100.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-trades-history)
    """
    data = {}
    if type is not None:
      data['type'] = type
    if trades is not None:
      data['trades'] = trades
    if start is not None:
      data['start'] = start
    if end is not None:
      data['end'] = end
    if ofs is not None:
      data['ofs'] = ofs
    if without_count is not None:
      data['without_count'] = without_count
    if consolidate_taker is not None:
      data['consolidate_taker'] = consolidate_taker
    if ledgers is not None:
      data['ledgers'] = ledgers
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier
    if aclass is not None:
      data['aclass'] = aclass
    if pair is not None:
      data['pair'] = pair
    if limit is not None:
      data['limit'] = limit

    return await self.authed_request(
      '/0/private/TradesHistory', data, validator=validate_trades_history
    )
