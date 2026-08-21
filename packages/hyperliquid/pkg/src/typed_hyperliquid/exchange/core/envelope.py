"""The `/exchange` response envelope: `{status: "ok", response}` or `{status: "err",
response}`. Kept as its own file because there are two independent failure signals for
an exchange action -- a non-2xx HTTP status (handled by the transport) and this embedded
`status` field.

Whether that embedded `status` is worth raising on splits by whether the action batches
per-item results (S9, `docs/production_standards.md`):

- The four batched actions (`order`, `cancel`, `cancel_by_cloid`, `modify_orders`) can
  return a top-level `status: "ok"` for the whole action while individual entries in
  `response.data.statuses` still carry a per-item `{"error": "..."}` (see
  `error_responses.md` in `spec/discovery.md`'s Transports section) -- there is no single
  top-level failure this envelope could raise on for those four without either hiding a
  real per-item error or false-positiving on a mixed-result batch. Their generated methods
  keep returning the whole `ExchangeResponse[T]` union unraised, and inspecting per-item
  results is left to each endpoint's own response type.
- Every other leaf action's response is a single, non-batched result -- `status: "err"`
  there really is the one failure signal, with nothing per-item it could be hiding or
  contradicting -- so their generated methods call `raise_on_error` below instead, which
  raises `typed_core.exceptions.ApiError` on `status: "err"` and otherwise returns just
  the unwrapped `response`, narrowing the return type from `ExchangeResponse[T]` to `T`.
"""

from typing_extensions import Any, Generic, Literal, Mapping, TypeVar
import pydantic

from typed_core.exceptions import ApiError
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


def raise_on_error(result: ExchangeResponse[T]) -> T:
  """Raise on a non-batched exchange action's `status: "err"`, else unwrap `response`.

  Args:
    result: The parsed (or, with validation off, raw) `{status, response}` envelope.

  Raises:
    ApiError: The venue reported `status: "err"` -- carries the raw `response` payload.
  """
  if result['status'] == 'err':
    raise ApiError(result['response'])
  return result['response']
