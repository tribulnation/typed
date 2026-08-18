from decimal import Decimal
from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Extra(TypedDict):
  daily: Decimal
  """Annual percentage yield for the daily reward type."""
  weekly: Decimal
  """Annual percentage yield for the weekly reward type."""
  monthly: Decimal
  """Annual percentage yield for the monthly reward type."""


validate_response = validator(dict[str, Extra])


class Apy(RpcEndpoint):
  async def apy(self, *, validate: bool | None = None) -> dict[str, Extra]:
    """Get current annual percentage yields by currency. Value of currency is an object wich reward type as a key and annual percentage yield as value

    Args:
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/earn/GET/v2/earn/apy)
    """
    return await self.request(
      'GET',
      '/v2/earn/apy',
      validator=validate_response,
      validate=validate,
    )
