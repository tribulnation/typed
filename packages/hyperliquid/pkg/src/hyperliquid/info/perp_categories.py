from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PerpCategoriesAction(TypedDict):
  type: Literal['perpCategories']


adapter = pydantic.TypeAdapter(list[tuple[str, str]])


class PerpCategories(InfoMixin):
  async def perp_categories(self) -> list[tuple[str, str]]:
    """Retrieve the category tag assigned to every perp coin across all perp dexs, as coin/category pairs.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: PerpCategoriesAction = {
      'type': 'perpCategories',
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
