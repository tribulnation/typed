"""`public/get_time` — `public/get_time`."""

from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_get_time = validator[int](int)


class GetTime(RpcEndpoint):
  """`public/get_time`."""

  async def get_time(self, *, validate: bool | None = None) -> int:
    """Retrieves the current time, in milliseconds since the UNIX epoch. Useful for checking the clock skew between the caller's software and Deribit's systems.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/supporting/public-get_time)
    """
    return await self.request(
      'public/get_time', validator=validate_get_time, validate=validate
    )
