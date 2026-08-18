from bit2me.core.endpoint import RpcEndpoint


class Delete(RpcEndpoint):
  async def delete(self, *, address_id: str, validate: bool | None = None):
    """Remove user address

    Args:
      address_id: The address id
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/DELETE/v1/account/address)
    """
    params: dict = {
      'addressId': address_id,
    }
    return await self.authed_request(
      'DELETE',
      '/v1/account/address',
      params=params,
      validate=validate,
    )
