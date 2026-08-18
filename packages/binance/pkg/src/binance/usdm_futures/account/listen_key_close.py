from binance.core.endpoint.rpc import RpcEndpoint


class ListenKeyClose(RpcEndpoint):
  """Close User Data Stream"""

  async def listen_key_close(self, *, validate: bool | None = None):
    """Close out a user data stream.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/user-data-streams#close-user-data-stream)
    """
    return await self.request('DELETE', '/fapi/v1/listenKey', validate=validate)
