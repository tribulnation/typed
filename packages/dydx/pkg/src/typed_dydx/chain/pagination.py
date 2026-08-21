"""Cosmos gRPC pagination helpers."""

from typing_extensions import Protocol

from typed_dydx.protos.cosmos.base.query import v1beta1 as query_proto

class HasPagination(Protocol):
  """Response carrying an optional Cosmos pagination payload."""
  pagination: query_proto.PageResponse | None

def page_request(
  key: bytes = b'', *, limit: int | None = None, reverse: bool = False,
) -> query_proto.PageRequest:
  """Build a Cosmos key-based page request.

  Args:
    key: Continuation key returned by the previous response.
    limit: Optional maximum number of items in the next page.
    reverse: Request descending order when the endpoint supports it.

  Returns:
    A Cosmos page request using efficient key-based pagination.
  """
  request = query_proto.PageRequest(key=key)
  if limit is not None:
    request.limit = limit
  if reverse:
    request.reverse = reverse
  return request

def next_key(response: HasPagination) -> bytes | None:
  """Return the next Cosmos page key when another page is available.

  Args:
    response: Response object with a Cosmos pagination field.

  Returns:
    The next page key, or `None` when pagination is complete.
  """
  pagination = response.pagination
  if pagination is None or not pagination.next_key:
    return None
  return pagination.next_key
