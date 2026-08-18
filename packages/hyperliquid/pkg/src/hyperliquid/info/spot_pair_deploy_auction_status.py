from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class SpotDeployGasAuction(TypedDict):
  startTimeSeconds: int
  """Auction start time, in seconds since epoch."""
  durationSeconds: int
  """Total auction duration, in seconds."""
  startGas: str
  """Gas price at the start of the auction, as a decimal string. Decays linearly toward `endGas` over `durationSeconds`."""
  currentGas: None | str
  """Gas price a deployment would pay right now, as a decimal string, while the auction is still in progress; `null` once the auction has ended."""
  endGas: None | str
  """Gas price the auction settled at, as a decimal string, once the auction has ended; `null` while still in progress."""


class SpotPairDeployAuctionStatusAction(TypedDict):
  type: Literal['spotPairDeployAuctionStatus']


adapter = pydantic.TypeAdapter(SpotDeployGasAuction)


class SpotPairDeployAuctionStatus(InfoMixin):
  async def spot_pair_deploy_auction_status(self) -> SpotDeployGasAuction:
    """Retrieve the status of the Dutch gas auction that prices `RegisterSpot` deployments -- pairing an already-existing base token with an already-existing quote token into a new tradable spot pair. This auction is independent from the one `spotDeployState` reports on for new token registration.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: SpotPairDeployAuctionStatusAction = {
      'type': 'spotPairDeployAuctionStatus',
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
