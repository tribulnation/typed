"""`private/logout` — `private/logout`."""

from deribit.core import RpcEndpoint


class Logout(RpcEndpoint):
  """`private/logout`."""

  async def logout(
    self,
    *,
    invalidate_token: bool | None = None,
    validate: bool | None = None,
  ):
    """Gracefully terminate the current WebSocket connection and optionally invalidate all tokens associated with the session. Orders are NOT cancelled by this graceful logout even when Cancel On Disconnect is enabled (unlike an unexpected disconnection, inactivity timeout, or heartbeat failure, which do cancel them).

    Args:
      invalidate_token: Default true: all tokens created during the current session are invalidated, requiring re-authentication on the next connection. False: tokens remain valid, so the same authentication can reconnect.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/authentication/private-logout)
    """
    params = {}
    if invalidate_token is not None:
      params['invalidate_token'] = invalidate_token
    return await self.authed_request('private/logout', params=params, validate=validate)
