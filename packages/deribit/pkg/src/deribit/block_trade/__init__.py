from .approve_block_trade import ApproveBlockTrade
from .get_block_trade import GetBlockTrade
from .get_block_trade_requests import GetBlockTradeRequests
from .get_block_trades import GetBlockTrades
from .get_broker_clients import GetBrokerClients
from .get_broker_trade_requests import GetBrokerTradeRequests
from .get_broker_trades import GetBrokerTrades
from .invalidate_block_trade_signature import InvalidateBlockTradeSignature
from .reject_block_trade import RejectBlockTrade


class BlockTrade(
  ApproveBlockTrade,
  GetBlockTrade,
  GetBlockTradeRequests,
  GetBlockTrades,
  GetBrokerClients,
  GetBrokerTradeRequests,
  GetBrokerTrades,
  InvalidateBlockTradeSignature,
  RejectBlockTrade,
):
  """BlockTrade endpoints."""
