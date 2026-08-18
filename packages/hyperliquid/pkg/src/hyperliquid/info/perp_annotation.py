from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PerpAnnotation(TypedDict):
  """Deployer-set annotation for a perp coin."""

  category: str
  """Category tag assigned to the coin (<=15 characters)."""
  description: str
  """Free-text description of the coin (<=400 characters)."""
  displayName: str | None
  """Short display name for the coin (<=9 characters), or `null` if unset."""
  keywords: list[str]
  """Search keywords for the coin (at most 2)."""


class PerpAnnotationAction(TypedDict):
  type: Literal['perpAnnotation']
  coin: str


adapter = pydantic.TypeAdapter(PerpAnnotation | None)


class PerpAnnotationEndpoint(InfoMixin):
  async def perp_annotation(self, *, coin: str) -> PerpAnnotation | None:
    """Retrieve the deployer-set annotation (category, description, display name, keywords) for a perp coin, if one has been set via the `setPerpAnnotation` HIP-3 action.

    Args:
      coin: Perp asset symbol to look up the annotation for.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: PerpAnnotationAction = {
      'type': 'perpAnnotation',
      'coin': coin,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
