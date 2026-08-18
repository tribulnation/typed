"""KuCoin Spot endpoints."""

from functools import cached_property

from .all_currencies import AllCurrencies
from .all_symbols import AllSymbols
from .all_tickers import AllTickers
from .announcements import Announcements
from .call_auction_info import CallAuctionInfoEndpoint
from .call_auction_part_orderbook import CallAuctionPartOrderbook
from .client_ip import ClientIp
from .currency import Currency
from .fiat_price import FiatPrice
from .full_orderbook import FullOrderbook
from .klines import Klines
from .kyc_regions import KycRegions
from .market_list import MarketList
from .oco_orders import OcoOrders
from .orders_hf import OrdersHf
from .part_orderbook import PartOrderbook
from .server_time import ServerTime
from .service_status import ServiceStatusEndpoint
from .stats_24h import Stats24h
from .stop_orders import StopOrders
from .symbol import Symbol
from .ticker import Ticker
from .trade_history import TradeHistory


class Spot(
  AllCurrencies,
  AllSymbols,
  AllTickers,
  Announcements,
  CallAuctionInfoEndpoint,
  CallAuctionPartOrderbook,
  ClientIp,
  Currency,
  FiatPrice,
  FullOrderbook,
  Klines,
  KycRegions,
  MarketList,
  PartOrderbook,
  ServerTime,
  ServiceStatusEndpoint,
  Stats24h,
  Symbol,
  Ticker,
  TradeHistory,
):
  """KuCoin Spot endpoints."""

  @cached_property
  def oco_orders(self) -> OcoOrders:
    """OcoOrders endpoints."""
    return OcoOrders(client=self.client)

  @cached_property
  def orders_hf(self) -> OrdersHf:
    """OrdersHf endpoints."""
    return OrdersHf(client=self.client)

  @cached_property
  def stop_orders(self) -> StopOrders:
    """StopOrders endpoints."""
    return StopOrders(client=self.client)
