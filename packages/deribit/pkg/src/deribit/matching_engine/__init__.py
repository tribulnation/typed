from .execute_block_trade import ExecuteBlockTrade
from .simulate_block_trade import SimulateBlockTrade
from .verify_block_trade import VerifyBlockTrade


class MatchingEngine(
  ExecuteBlockTrade,
  SimulateBlockTrade,
  VerifyBlockTrade,
):
  """MatchingEngine endpoints."""
