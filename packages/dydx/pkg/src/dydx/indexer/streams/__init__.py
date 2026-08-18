"""Grouped WebSocket indexer streams."""

from dataclasses import dataclass

from .core import INDEXER_WS_URL, INDEXER_TESTNET_WS_URL
from .block_height import BlockHeight
from .candles import Candles
from .markets import Markets
from .orders import Orders
from .parent_subaccounts import ParentSubaccounts
from .subaccounts import Subaccounts
from .trades import Trades


@dataclass
class IndexerStreams(
  BlockHeight,
  Candles,
  Markets,
  Orders,
  ParentSubaccounts,
  Subaccounts,
  Trades,
):
  """WebSocket indexer stream endpoint group."""
