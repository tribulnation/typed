"""REST v2 transport (gateway v2 and archive v2): plain `GET`s answered with bare JSON."""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..endpoint.rest import RestClient
from ..envelope import unwrap_bare
from .http import get_json

T = TypeVar('T')


@dataclass(kw_only=True)
class RestTransport(RestClient):
  """The gateway v2 or archive v2 market-data API."""

  http: HttpClient
  """The client's shared HTTP connection pool."""
  base_url: str
  """The v2 base every path hangs off."""
  validate: bool = True
  """Validate responses by default."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def get(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """`GET` one path; see `RestClient.get`.

    Raises:
      BadRequest: The venue refused the request (HTTP `400` with an error code).
      ApiError: Any other venue error.
    """
    result = unwrap_bare(await get_json(self.http, self.base_url + path, params))
    if validator is not None and self.should_validate(validate):
      return validator.python(result)
    return result
