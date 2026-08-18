"""The `/exchange` response envelope: `{status: "ok", response}` or `{status: "err",
response}`. Kept as its own file because there are two independent failure signals for
an exchange action -- a non-2xx HTTP status (handled by the transport) and this embedded
`status` field.

Deliberately unwrapped no further than `{status, response}`, matching current, tested
behavior: batched order/cancel/modify actions can return `status: "ok"` for the whole
action while individual entries in `response.data.statuses` still carry a per-item
`{"error": "..."}` (see `error_responses.md` in `spec/discovery.md`'s Transports section)
-- there is no single top-level failure this envelope could raise on without either
hiding a real per-item error or false-positiving on a mixed-result batch. Inspecting
per-item results is left to each endpoint's own response type.
"""

from typing_extensions import Any, Generic, Literal, Mapping, TypeVar
import pydantic

from typed_core.validation import TypedDict

T = TypeVar('T', default=Any)


class ExchangeRequest(TypedDict):
  action: Mapping[str, Any]
  nonce: int
  signature: Mapping[str, Any]
  vaultAddress: str | None
  expiresAfter: int | None


class OkResponse(TypedDict, Generic[T]):
  status: Literal['ok']
  response: T


class ErrorResponse(TypedDict):
  status: Literal['err']
  response: Any


ExchangeResponse = OkResponse[T] | ErrorResponse

response_adapter = pydantic.TypeAdapter(ExchangeResponse)
