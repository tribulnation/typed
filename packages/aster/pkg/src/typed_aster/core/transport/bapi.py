"""HTTP transport for BAPI, the public API of Aster's web backend (`www.asterdex.com/bapi`).

Every reply is wrapped as `{code, message, messageDetail, data, success}`. Success is
`success: true` with code `"000000"`, and the result is `data`. Failure arrives either as
an HTTP `4XX` (`{"code": "000002", "message": "For input string: \\"x\\""}`) or as HTTP
200 with `success: false` (`{"code": "400", "message": "Unsupport token"}`). BAPI serves
public calls only, and has no testnet.
"""

from typing_extensions import Any, Mapping, NotRequired, TypeVar
from dataclasses import dataclass, field

import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, ValidationError
from typed_core.http import HttpClient
from typed_core.validation import TypedDict, validator

from ..auth import Wallet
from ..endpoint.rpc import Meta, RpcClient
from ..envelope import decode, raise_error
from ..urls import BAPI_URL
from .http import encode

T = TypeVar('T')

SUCCESS_CODE = '000000'


class Envelope(TypedDict):
  """A BAPI reply."""

  code: str
  message: str | None
  messageDetail: NotRequired[str | None]
  data: Any
  success: bool


validate_envelope = validator(Envelope)


def unwrap(response: httpx.Response) -> Any:
  """Return the `data` of a BAPI reply.

  Raises:
    BadRequest: A rejected request: an HTTP `4XX`, or `success: false` with a `4XX` code.
    ApiError: Any other failure.
    ValidationError: The body is not a BAPI reply.
  """
  try:
    payload = decode(response.content)
  except ValueError:
    payload = response.text
  if not response.is_success:
    raise_error(response.status_code, payload)
  envelope = validate_envelope.python(payload)
  if envelope['success'] and envelope['code'] == SUCCESS_CODE:
    return envelope['data']
  code = envelope['code']
  if code.isdigit() and 400 <= int(code) < 500:
    raise BadRequest(code, envelope['message'], envelope)
  raise ApiError(code, envelope['message'], envelope)


@dataclass(kw_only=True)
class BapiClient(RpcClient):
  """HTTP client for BAPI. Parameters travel in the query string, as on every Aster
  REST surface."""

  base_url: str = BAPI_URL
  """BAPI root; paths are relative to it, e.g. `futures/v1/public/future/aster/deposit/assets`."""
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one public request and return its `data`, validated unless disabled."""
    query = encode(list((params or {}).items()))
    url = f'{self.base_url}/{path}'
    response = await self.http.request(method, f'{url}?{query}' if query else url)
    payload = unwrap(response)
    if validator is not None and (self.validate if validate is None else validate):
      return validator.python(payload)
    return payload

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    meta: Meta,
    params: Mapping[str, Any] | None = None,
    child: Wallet | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """BAPI has no signed calls.

    Raises:
      AuthError: Always.
    """
    raise AuthError(
      'BAPI serves public calls only: declare its endpoints `sign: none`.'
    )
