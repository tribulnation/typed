"""Edge transport: GRVT's REST host (`https://edge.{env}`) for referral, deposit and bridge.

Bodies are bare JSON with no envelope; failures are plain HTTP statuses. Calls carry the
shared session unless `EdgeMeta.public` says the endpoint needs none.
"""

from dataclasses import dataclass, field
from types import UnionType
import json

import httpx
from typing_extensions import Any, TypeVar

from typed_core.exceptions import AuthError, LogicError
from typed_core.http import HttpClient

from ..auth import Session
from ..endpoint.edge import EdgeClient, EdgeMeta
from ..envelope import check_edge, decode
from ..owners import Connection, Owned
from ..wire import dump, fill, load

T = TypeVar('T')


def session_rejected(response: httpx.Response) -> bool:
  """Whether an edge response is the venue rejecting the session: a `401` with a JSON object
  body (`{"code": "err_auth_...", ...}`).

  A non-JSON `401` is a Cloudflare/WAF block page, not the venue: logging in again would not
  help, so it is raised as is (`envelope.raise_unparsed`, `ApiError("Blocked by ...")`).
  """
  return response.status_code == 401 and isinstance(decode(response), dict)


@dataclass(kw_only=True)
class EdgeTransport(Owned, EdgeClient):
  """The edge host: REST calls, authenticated by the shared session.

  Its `HttpClient` closes when its last owner leaves (`Owned`), and it takes one ownership
  of the session while owned itself. So an `async with client.edge` nested inside `async
  with client` keeps the connection pool open for the outer block, and for any edge call
  still in flight; the outermost exit closes it.
  """

  base_url: str
  """Edge base URL, e.g. `https://edge.grvt.io`."""
  http: HttpClient = field(default_factory=HttpClient)
  session: Session | None = None
  """Session for authenticated calls; `None` on a public client."""
  validate: bool = True

  def connections(self) -> list[Connection]:
    """The edge HTTP pool, closed when the last owner leaves."""
    return [self.http]

  def shared(self) -> list[Owned]:
    """The session, owned once more while this transport is owned."""
    return [] if self.session is None else [self.session]

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: EdgeMeta | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Call one edge endpoint; see `EdgeEndpoint.request` for the arguments.

    A JSON `401` on a call that sent a session logs in again and retries once; a non-JSON
    `401` (a block page) is never retried.

    Raises:
      AuthError: The endpoint needs a session and this client has none, or it was rejected
        again after logging in.
      ApiError: A non-JSON `401`/`403` (`"Blocked by ..."`), never retried.
      BadRequest: The request does not match `request_type` (see `wire.dump`); nothing is
        sent.
      RateLimited, BadRequest, ApiError: Any other error response; see
        `envelope.check_edge`.
    """
    public = bool((meta or {}).get('public'))
    if not public and self.session is None:
      raise AuthError('No credentials: this edge endpoint needs a session')
    wire = dump(request, request_type, operation=f'{method} {path}')
    url_path, rest = fill(path, wire or {})
    url = self.base_url + url_path
    params = rest if method == 'GET' and rest else None
    content = json.dumps(rest, separators=(',', ':')) if method != 'GET' else None
    session = None if public else self.session
    for attempt in (1, 2):
      state = None if session is None else await session.state()
      response = await self.http.request(
        method,
        url,
        params=params,
        content=content,
        headers={
          **({'Content-Type': 'application/json'} if content is not None else {}),
          **(state.headers if state is not None else {}),
        },
      )
      if (
        session is not None
        and state is not None
        and attempt == 1
        and session_rejected(response)
      ):
        # A session the edge host no longer accepts: log in again, once.
        session.invalidate(state)
        continue
      body = check_edge(response)
      validate = self.validate if validate is None else validate
      return load(body, response_type, validate=validate)
    raise LogicError('unreachable')
