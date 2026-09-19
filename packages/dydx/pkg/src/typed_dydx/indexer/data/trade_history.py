"""Trade history queries with paired market filters and typed pagination."""

from typed_core import PaginatedResponse
from typing_extensions import overload

from typed_dydx.indexer.schemas import MarketType, TradeHistory, TradeHistoryResponse

from .core import IndexerMixin
from .get_parent_trade_history import GetParentTradeHistory
from .get_trade_history import GetTradeHistory


def validate_market_filter(market: str | None, market_type: MarketType | None):
  """Require the market ticker and market type to be supplied together."""
  if (market is None) != (market_type is None):
    raise ValueError('market and market_type must be provided together')


class TradeHistoryMethods(IndexerMixin):
  """Trade history methods for a subaccount, with paired market filters."""

  @overload
  async def get_trade_history(
    self,
    *,
    address: str,
    subaccount: int,
    market: None = None,
    market_type: None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> TradeHistoryResponse: ...

  @overload
  async def get_trade_history(
    self,
    *,
    address: str,
    subaccount: int,
    market: str,
    market_type: MarketType,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> TradeHistoryResponse: ...

  async def get_trade_history(
    self,
    *,
    address: str,
    subaccount: int,
    market: str | None = None,
    market_type: MarketType | None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> TradeHistoryResponse:
    """Fetch position actions for a subaccount, newest first.

    Fees and realized PnL are cumulative within each position lifecycle; summing
    rows double-counts them. Realized PnL excludes fees and funding, and its
    percentage field is a ratio. Child subaccounts have independent lifecycles.

    Args:
      address: Wallet address that owns the account.
      subaccount: Subaccount number.
      market: Market ticker; supply together with market_type.
      market_type: Market type; supply together with market.
      limit: Maximum rows requested per page.
      page: One-based page number; omit to request the first page.
      validate: Override response validation for this call.

    Raises:
      ValueError: Exactly one of market and market_type is supplied.

    References:
      - [dYdX trade history controller](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/controllers/api/v4/trade-history-controller.ts)
      - [dYdX trade history accounting](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/lib/trade-history.ts)
    """
    validate_market_filter(market, market_type)
    endpoint = GetTradeHistory(client=self.client)
    return await endpoint.get_trade_history(
      address=address,
      subaccount=subaccount,
      market=market,
      market_type=market_type,
      limit=limit,
      page=page,
      validate=validate,
    )

  @overload
  def get_trade_history_paged(
    self,
    *,
    address: str,
    subaccount: int,
    market: None = None,
    market_type: None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TradeHistory, int]: ...

  @overload
  def get_trade_history_paged(
    self,
    *,
    address: str,
    subaccount: int,
    market: str,
    market_type: MarketType,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TradeHistory, int]: ...

  def get_trade_history_paged(
    self,
    *,
    address: str,
    subaccount: int,
    market: str | None = None,
    market_type: MarketType | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TradeHistory, int]:
    """Page through position actions for a subaccount.

    Fees and realized PnL are cumulative within each position lifecycle; summing
    rows double-counts them. Realized PnL excludes fees and funding, and its
    percentage field is a ratio. Child subaccounts have independent lifecycles.

    Await the result to collect rows, or iterate asynchronously over pages.

    Args:
      address: Wallet address that owns the account.
      subaccount: Subaccount number.
      market: Market ticker; supply together with market_type.
      market_type: Market type; supply together with market.
      limit: Maximum rows requested per page.
      validate: Override response validation for this call.

    Raises:
      ValueError: Exactly one of market and market_type is supplied.

    References:
      - [dYdX trade history controller](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/controllers/api/v4/trade-history-controller.ts)
      - [dYdX trade history accounting](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/lib/trade-history.ts)
    """
    validate_market_filter(market, market_type)
    endpoint = GetTradeHistory(client=self.client)
    return endpoint.get_trade_history_paged(
      address=address,
      subaccount=subaccount,
      market=market,
      market_type=market_type,
      limit=limit,
      validate=validate,
    )


class ParentTradeHistoryMethods(IndexerMixin):
  """Trade history methods for a parent subaccount and its children, with paired market filters."""

  @overload
  async def get_parent_trade_history(
    self,
    *,
    address: str,
    parent_subaccount: int,
    market: None = None,
    market_type: None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> TradeHistoryResponse: ...

  @overload
  async def get_parent_trade_history(
    self,
    *,
    address: str,
    parent_subaccount: int,
    market: str,
    market_type: MarketType,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> TradeHistoryResponse: ...

  async def get_parent_trade_history(
    self,
    *,
    address: str,
    parent_subaccount: int,
    market: str | None = None,
    market_type: MarketType | None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> TradeHistoryResponse:
    """Fetch position actions for a parent subaccount and its children, newest first.

    Fees and realized PnL are cumulative within each position lifecycle; summing
    rows double-counts them. Realized PnL excludes fees and funding, and its
    percentage field is a ratio. Child subaccounts have independent lifecycles.

    Args:
      address: Wallet address that owns the account.
      parent_subaccount: Parent subaccount number.
      market: Market ticker; supply together with market_type.
      market_type: Market type; supply together with market.
      limit: Maximum rows requested per page.
      page: One-based page number; omit to request the first page.
      validate: Override response validation for this call.

    Raises:
      ValueError: Exactly one of market and market_type is supplied.

    References:
      - [dYdX trade history controller](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/controllers/api/v4/trade-history-controller.ts)
      - [dYdX trade history accounting](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/lib/trade-history.ts)
    """
    validate_market_filter(market, market_type)
    endpoint = GetParentTradeHistory(client=self.client)
    return await endpoint.get_parent_trade_history(
      address=address,
      parent_subaccount=parent_subaccount,
      market=market,
      market_type=market_type,
      limit=limit,
      page=page,
      validate=validate,
    )

  @overload
  def get_parent_trade_history_paged(
    self,
    *,
    address: str,
    parent_subaccount: int,
    market: None = None,
    market_type: None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TradeHistory, int]: ...

  @overload
  def get_parent_trade_history_paged(
    self,
    *,
    address: str,
    parent_subaccount: int,
    market: str,
    market_type: MarketType,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TradeHistory, int]: ...

  def get_parent_trade_history_paged(
    self,
    *,
    address: str,
    parent_subaccount: int,
    market: str | None = None,
    market_type: MarketType | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[TradeHistory, int]:
    """Page through position actions for a parent subaccount and its children.

    Fees and realized PnL are cumulative within each position lifecycle; summing
    rows double-counts them. Realized PnL excludes fees and funding, and its
    percentage field is a ratio. Child subaccounts have independent lifecycles.

    Await the result to collect rows, or iterate asynchronously over pages.

    Args:
      address: Wallet address that owns the account.
      parent_subaccount: Parent subaccount number.
      market: Market ticker; supply together with market_type.
      market_type: Market type; supply together with market.
      limit: Maximum rows requested per page.
      validate: Override response validation for this call.

    Raises:
      ValueError: Exactly one of market and market_type is supplied.

    References:
      - [dYdX trade history controller](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/controllers/api/v4/trade-history-controller.ts)
      - [dYdX trade history accounting](https://github.com/dydxprotocol/v4-chain/blob/3680d421f83f9f53ef7f5472e8970b7b455664f8/indexer/services/comlink/src/lib/trade-history.ts)
    """
    validate_market_filter(market, market_type)
    endpoint = GetParentTradeHistory(client=self.client)
    return endpoint.get_parent_trade_history_paged(
      address=address,
      parent_subaccount=parent_subaccount,
      market=market,
      market_type=market_type,
      limit=limit,
      validate=validate,
    )
