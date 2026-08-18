"""dYdX indexer miscellaneous account types."""

from typing_extensions import TypedDict
from .positions import PerpetualPosition, AssetPosition

class Account(TypedDict):
  """Account payload.

  References:
    - [dYdX API docs](https://docs.dydx.xyz/types/account)
  """
  address: str
  subaccountNumber: int


class Subaccount(TypedDict):
  """Subaccount payload."""
  address: str
  subaccountNumber: int
  equity: str
  freeCollateral: str
  openPerpetualPositions: dict[str, PerpetualPosition]
  assetPositions: dict[str, AssetPosition]
  marginEnabled: bool
  updatedAtHeight: str
  latestProcessedBlockHeight: str
