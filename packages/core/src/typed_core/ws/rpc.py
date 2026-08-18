from typing_extensions import Any, TypeVar, Generic, TypedDict
from abc import abstractmethod
from dataclasses import dataclass, field
import asyncio

from .socket import Socket

Request = TypeVar('Request', default=Any)
Reply = TypeVar('Reply', default=Any)

class Response(TypedDict, Generic[Reply]):
  id: int
  reply: Reply

@dataclass
class Rpc(Socket, Generic[Request, Reply]):
  """Multiplexed request/response client via message IDs.
  
  ### Features
  - Internal ID management
  - `rpc_request` for RPC request/response agnostic to IDs

  ### Requires implementing
  - `parse_response` to parse an incoming message into the ID and reply
  - `rpc_send` to send an identified request to the server

  ### Concurrency Contract
  1. Connection: single owner via `async with`, also supports lazy no-owner use
  2. Requests: many concurrent `rpc_request()` calls OK
  """
  replies: dict[int, asyncio.Future[Reply]] = field(default_factory=dict)
  counter: int = 0

  @abstractmethod
  def parse_response(self, msg: str | bytes) -> Response[Reply] | None:
    ...

  @abstractmethod
  async def rpc_send(self, id: int, req: Request):
    ...

  def on_msg(self, msg: str | bytes):
    response = self.parse_response(msg)
    if response is not None:
      self.replies[response['id']].set_result(response['reply'])

  async def rpc_request(self, request: Request) -> Reply:
    id = self.counter
    self.counter += 1
    self.replies[id] = asyncio.Future()
    await self.rpc_send(id, request)
    response = await self.wait(self.replies[id])
    del self.replies[id]
    return response
