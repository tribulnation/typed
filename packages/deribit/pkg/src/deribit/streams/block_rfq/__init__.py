from .block_trade_confirmations import BlockTradeConfirmations
from .block_trade_confirmations_by_currency import BlockTradeConfirmationsByCurrency
from .maker import Maker
from .maker_quotes import MakerQuotes
from .taker import Taker
from .trades import Trades


class BlockRfq(
  BlockTradeConfirmations,
  BlockTradeConfirmationsByCurrency,
  Maker,
  MakerQuotes,
  Taker,
  Trades,
):
  """BlockRfq endpoints."""
