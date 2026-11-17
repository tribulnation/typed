"""HTTP plumbing every Nado REST transport shares: the mandatory compression header, JSON
`POST`/`GET` and the status check."""

from typing_extensions import Any, Mapping

from typed_core.http import HttpClient

from ..envelope import check_http

HEADERS = {'Accept-Encoding': 'gzip, deflate'}
"""Sent on every request: Nado answers `403` to a request whose `Accept-Encoding` lacks
`gzip`, `br` or `deflate`."""


async def post_json(
  http: HttpClient, url: str, body: Any, *, timeout: float | None = None
) -> Any:
  """`POST` a JSON body and return the decoded response, raising on an unusable status.

  Args:
    http: The shared HTTP client.
    url: Full URL.
    body: JSON body.
    timeout: This request's timeout in seconds; the client's default when `None`.
  """
  if timeout is None:
    response = await http.request('POST', url, json=body, headers=HEADERS)
  else:
    response = await http.request(
      'POST', url, json=body, headers=HEADERS, timeout=timeout
    )
  return check_http(response)


async def get_json(
  http: HttpClient, url: str, params: Mapping[str, Any] | None = None
) -> Any:
  """`GET` a URL and return the decoded response, raising on an unusable status.

  Args:
    http: The shared HTTP client.
    url: Full URL.
    params: Query string values; booleans go as `true`/`false`, lists as repeated keys.
  """
  response = await http.request(
    'GET', url, params=query_values(params or {}), headers=HEADERS
  )
  return check_http(response)


def query_values(values: Mapping[str, Any]) -> dict[str, str | list[str]]:
  """Flatten values for a query string: booleans as `true`/`false`, lists as repeated keys,
  `None` dropped."""

  def scalar(value: Any) -> str:
    """One query value as a string."""
    if isinstance(value, bool):
      return 'true' if value else 'false'
    return str(value)

  flat: dict[str, str | list[str]] = {}
  for key, value in values.items():
    if value is None:
      continue
    if isinstance(value, list | tuple):
      flat[key] = [scalar(item) for item in value if item is not None]
    else:
      flat[key] = scalar(value)
  return flat
