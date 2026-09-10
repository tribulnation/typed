"""WebSocket transport for `exchange` (wallet-signed) requests -- a thin adapter over the
shared, multiplexed `SocketClient` connection also used by `info` and `streams`.
"""

from typing_extensions import Any, Mapping
from dataclasses import dataclass

from typed_core.exceptions import ApiError

from typed_hyperliquid.core.endpoint.rpc import RpcClient
from typed_hyperliquid.core.ws import SocketClient


@dataclass(kw_only=True)
class ExchangeSocketClient(RpcClient):
  """WebSocket transport for Hyperliquid exchange (signed) requests.

  `payload` is an `ExchangeRequest` in practice -- see `transport/http.py` for why the
  parameter is kept as the wider `Mapping[str, Any]` instead. Returns the decoded
  `{status, response}` envelope verbatim, unvalidated -- see `transport/http.py`'s own
  docstring for why: `ExchangeCore.request` is the one place that validates now.
  """

  ws: SocketClient

  async def request(self, payload: Mapping[str, Any]) -> Any:
    reply = await self.ws.rpc_request({'type': 'action', 'payload': payload})
    if reply['type'] == 'action':
      return reply['payload']
    elif reply['type'] == 'error':
      raise ApiError(reply['payload'])
    else:
      raise ApiError(f'Unexpected reply type: {reply["type"]}', reply['payload'])

  async def __aenter__(self):
    await self.ws.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.ws.__aexit__(exc_type, exc_value, traceback)
