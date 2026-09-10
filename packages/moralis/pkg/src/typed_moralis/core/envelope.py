"""Moralis's single response envelope: bare JSON on success, an error payload
otherwise, with HTTP status the only failure discriminator -- shared by every product
this client implements.
"""

from typing_extensions import Any
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited


def raise_http_status(response: httpx.Response):
  """Raise the `typed_core` exception matching a non-2xx HTTP status.

  Args:
    response: The unsuccessful HTTP response.

  Raises:
    AuthError: Status `401` or `403`.
    RateLimited: Status `429`.
    BadRequest: Any other `4xx` status.
    ApiError: Any other unsuccessful status.
  """
  try:
    payload: Any = response.json()
  except ValueError:
    payload = response.text
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  if status == 429:
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)


def unwrap_rest(response: httpx.Response) -> Any:
  """Return the parsed JSON body of a Moralis response.

  Args:
    response: The HTTP response to unwrap.

  Raises:
    ApiError: The HTTP status was unsuccessful (via `raise_http_status`).
  """
  if not response.is_success:
    raise_http_status(response)
  return response.json()
