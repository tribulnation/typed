"""KuCoin Margin endpoints."""

from functools import cached_property

from .config import Config
from .credit import Credit
from .cross_margin_symbols import CrossMarginSymbolsEndpoint
from .debit import Debit
from .isolated_margin_symbols import IsolatedMarginSymbols
from .mark_price_detail import MarkPriceDetail
from .mark_price_list import MarkPriceList
from .market import Market
from .oco_orders import OcoOrders
from .orders_hf import OrdersHf
from .risk_limit import RiskLimit
from .stop_orders import StopOrders


class Margin(
  Config,
  CrossMarginSymbolsEndpoint,
  IsolatedMarginSymbols,
  MarkPriceDetail,
  MarkPriceList,
):
  """KuCoin Margin endpoints."""

  @cached_property
  def credit(self) -> Credit:
    """Credit endpoints."""
    return Credit(client=self.client)

  @cached_property
  def debit(self) -> Debit:
    """Debit endpoints."""
    return Debit(client=self.client)

  @cached_property
  def market(self) -> Market:
    """Market endpoints."""
    return Market(client=self.client)

  @cached_property
  def oco_orders(self) -> OcoOrders:
    """OcoOrders endpoints."""
    return OcoOrders(client=self.client)

  @cached_property
  def orders_hf(self) -> OrdersHf:
    """OrdersHf endpoints."""
    return OrdersHf(client=self.client)

  @cached_property
  def risk_limit(self) -> RiskLimit:
    """RiskLimit endpoints."""
    return RiskLimit(client=self.client)

  @cached_property
  def stop_orders(self) -> StopOrders:
    """StopOrders endpoints."""
    return StopOrders(client=self.client)
