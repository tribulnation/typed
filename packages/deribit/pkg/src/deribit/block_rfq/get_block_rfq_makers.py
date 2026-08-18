"""`private/get_block_rfq_makers` — `private/get_block_rfq_makers`."""

from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_get_block_rfq_makers = validator[list[str]](list[str])


class GetBlockRfqMakers(RpcEndpoint):
  """`private/get_block_rfq_makers`."""

  async def get_block_rfq_makers(self, *, validate: bool | None = None) -> list[str]:
    """Returns a list of all available Block RFQ makers. Takes no parameters. Use this to see which aliases can be targeted by `private/create_block_rfq`'s `makers` list.

    Scope: `block_rfq:read`.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-rfq/private-get_block_rfq_makers)
    """
    return await self.authed_request(
      'private/get_block_rfq_makers',
      validator=validate_get_block_rfq_makers,
      validate=validate,
    )
