from bit2me.core.endpoint import RpcEndpoint


class Delete(RpcEndpoint):
  async def __call__(self, *, validate: bool | None = None) -> None:
    """Delete user account

    Args:
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/DELETE/v1/account)
    """
    return await self.authed_request(
      'DELETE',
      '/v1/account',
      validate=validate,
    )
