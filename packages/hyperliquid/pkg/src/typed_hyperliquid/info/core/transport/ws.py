"""WebSocket transport for `info` requests -- a thin adapter over the shared, multiplexed
`SocketClient` connection also used by `exchange` and `streams`.
"""

from typing_extensions import Any, Mapping
from dataclasses import dataclass

from typed_core.exceptions import ApiError

from typed_hyperliquid.core.endpoint.rpc import RpcClient
from typed_hyperliquid.core.ws import SocketClient


@dataclass(kw_only=True)
class InfoSocketClient(RpcClient):
  """WebSocket transport for Hyperliquid info requests."""

  ws: SocketClient

  async def request(self, payload: Mapping[str, Any]) -> Any:
    reply = await self.ws.rpc_request({'type': 'info', 'payload': payload})
    if reply['type'] == 'info':
      return reply['payload']['data']
    elif reply['type'] == 'error':
      raise ApiError(reply['payload'])
    else:
      raise ApiError(f'Unexpected reply type: {reply["type"]}', reply['payload'])

  async def __aenter__(self):
    await self.ws.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.ws.__aexit__(exc_type, exc_value, traceback)
