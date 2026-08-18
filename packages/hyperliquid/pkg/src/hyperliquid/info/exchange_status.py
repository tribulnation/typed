from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class ExchangeStatusAction(TypedDict):
  type: Literal['exchangeStatus']


class ExchangeStatusResponse(TypedDict):
  """The exchange's current operational status."""

  specialStatuses: list[str] | None
  """Active special or maintenance statuses, or `null` when none are in effect."""
  time: int
  """Server's current time, as a millisecond Unix epoch timestamp."""


adapter = pydantic.TypeAdapter(ExchangeStatusResponse)


class ExchangeStatus(InfoMixin):
  async def exchange_status(self) -> ExchangeStatusResponse:
    """Retrieve the venue's current operational status: any special/maintenance statuses in effect, and the server's current time. Named only in the rate-limits doc's weight table (weight 2, alongside `l2Book`/`allMids`/`clearinghouseState`/`orderStatus`/`spotClearinghouseState`), not documented on the main info-endpoint page; see `notes`.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits)
    """
    params: ExchangeStatusAction = {
      'type': 'exchangeStatus',
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
