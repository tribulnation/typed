"""Base endpoint class for private (listenKey-based) user-data stream endpoints: design
§2/§8's single `subscribe()` verb, connect-only per rule 11's `push: {"trigger":
"connect"}` (this client is rule 11's own motivating example). No `meta` schema declared
for this core (`codegen/config.toml` `[cores.private_stream]` is absent) -- every endpoint
resolving here declares `meta: {}`; which listenKey-minting REST call feeds it is a
documentation fact recorded in `notes`, not a per-call quirk.

`subscribe()` takes `listen_key` directly, as a plain `str` -- not a `channel` template
plus a separate `parameters`/`request_type` pair. An earlier version took the general
`(channel, parameters, *, request_type, ...)` shape every other stream core's
`subscribe()` takes, and "filled `channel`'s own placeholder from `parameters`" the way
`design §8` describes for the ordinary case -- except there was no real channel to route
on here (connecting with a live listenKey already *is* the subscription), so `channel`
was passed through unread except into an error message, and the actual value extraction
hardcoded the wire field name `'listenKey'` rather than genuinely parsing `channel`'s
placeholder. `common/lib/src/typed_dev/codegen/python.py`'s `Generator.stream_endpoint`
now detects this exact shape (`_connect_channel_param`: a connect-only push whose
`channel` template is entirely one placeholder matching its one required parameter) and
generates the simplified call below directly, so there is no template/wrapper
indirection left to get out of sync with what this method actually reads.
"""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class PrivateStreamClient(Protocol):
  """Structural interface a transport implements to back a `PrivateStreamEndpoint`.

  Unlike `StreamClient.subscribe`, there is no channel to name: connecting with a live
  listenKey already embedded in the URL path *is* the subscription, and the server starts
  pushing whichever of several event types occur, with no way to select a subset (see
  `spec/core.md`'s WebSocket section).
  """

  def connect(
    self,
    listen_key: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Open one private user-data connection for `listen_key`, validating each pushed
    event against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class PrivateStreamEndpoint:
  """Base class for private (listenKey-based) user-data stream endpoints."""

  client: PrivateStreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    listen_key: str,
    *,
    validate: bool | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Open the one private user-data connection for `listen_key` -- no subscribe frame
    is ever sent (rule 11's `push: {"trigger": "connect"}`); connecting with a live
    listenKey already embedded in the URL path *is* the subscription.

    Args:
      listen_key: The live listenKey to connect with.
      validate: Per-call override of pushed-event validation.
      response_type: The generated payload type, used to validate each push.
    """
    if not listen_key:
      raise ValueError('listen_key is required')
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    manager = self.client.connect(listen_key, validator=response_validator, validate=validate)
    return manager  # type: ignore[return-value]
