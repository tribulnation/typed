from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class ApprovedBuildersAction(TypedDict):
  type: Literal['approvedBuilders']
  user: str


adapter = pydantic.TypeAdapter(list[str])


class ApprovedBuilders(InfoMixin):
  async def approved_builders(self, *, user: str) -> list[str]:
    """Retrieve the builder addresses a user has approved -- addresses only, not fee caps; the address-list counterpart to `maxBuilderFee`, which checks one builder's fee cap at a time.

    Args:
      user: Address of the user whose approved builders to list, as a 42-character hexadecimal string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: ApprovedBuildersAction = {
      'type': 'approvedBuilders',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
