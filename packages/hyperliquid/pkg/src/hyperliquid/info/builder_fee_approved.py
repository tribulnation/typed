from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class BuilderFeeApprovedAction(TypedDict):
  type: Literal['maxBuilderFee']
  user: str
  builder: str


adapter = pydantic.TypeAdapter(int)


class BuilderFeeApproved(InfoMixin):
  async def builder_fee_approved(self, *, user: str, builder: str) -> int:
    """Check the maximum builder fee a user has approved for a given builder address. Returns `0` when the user has not approved this builder at all.

    Args:
      user: Address of the user granting builder-fee approval, as a 42-character hexadecimal string.
      builder: Address of the builder to check approval for, as a 42-character hexadecimal string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: BuilderFeeApprovedAction = {
      'type': 'maxBuilderFee',
      'user': user,
      'builder': builder,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
