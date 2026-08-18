from .accept_block_rfq import AcceptBlockRfq
from .add_block_rfq_quote import AddBlockRfqQuote
from .cancel_all_block_rfq_quotes import CancelAllBlockRfqQuotes
from .cancel_block_rfq import CancelBlockRfq
from .cancel_block_rfq_quote import CancelBlockRfqQuote
from .cancel_block_rfq_trigger import CancelBlockRfqTrigger
from .create_block_rfq import CreateBlockRfq
from .edit_block_rfq_quote import EditBlockRfqQuote
from .get_block_rfq_makers import GetBlockRfqMakers
from .get_block_rfq_quotes import GetBlockRfqQuotes
from .get_block_rfq_trades import GetBlockRfqTrades
from .get_block_rfq_user_info import GetBlockRfqUserInfo
from .get_block_rfqs import GetBlockRfqs


class BlockRfq(
  AcceptBlockRfq,
  AddBlockRfqQuote,
  CancelAllBlockRfqQuotes,
  CancelBlockRfq,
  CancelBlockRfqQuote,
  CancelBlockRfqTrigger,
  CreateBlockRfq,
  EditBlockRfqQuote,
  GetBlockRfqMakers,
  GetBlockRfqQuotes,
  GetBlockRfqTrades,
  GetBlockRfqUserInfo,
  GetBlockRfqs,
):
  """BlockRfq endpoints."""
