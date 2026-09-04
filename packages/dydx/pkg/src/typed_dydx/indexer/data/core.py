"""dYdX Indexer HTTP transport (design §2/§5/§6, 2026-08-31 codegen mechanization).

`IndexerHttpClient` is the shared transport every Indexer HTTP leaf's resolved core
(`IndexerMixin`) forwards through. Indexer HTTP wraps some, but not all, of its responses
in a small envelope (`{positions: [...]}`, `{rewards: [...]}`, ...) -- which key (if any)
wraps the value a given call returns genuinely varies endpoint to endpoint, so it's a real
per-call `meta` fact (`codegen/config.toml` `[cores.data].meta`), not a fixed core convention the
way Comet's `result`/gRPC's proto envelope are.
"""

import json
from dataclasses import dataclass, field
from typing_extensions import Any, NotRequired, Self, TypedDict, TypeVar, cast
from types import UnionType

from typed_core import ApiError
from typed_core.exceptions import BadRequest, RateLimited
from typed_core.http import HttpClient
from typed_core.util import path_join
from typed_core.validation import validator

T = TypeVar('T')

INDEXER_HTTP_URL = 'https://indexer.dydx.trade/'
INDEXER_TESTNET_HTTP_URL = 'https://indexer.v4testnet.dydx.exchange'


class Meta(TypedDict):
  """`data`'s own `meta` shape (`codegen/config.toml` `[cores.data].meta`): the dotted wire key
  wrapping the value this call returns, when the indexer wraps one. Hand-written to match
  that declared JSON Schema -- never code-generated (design §2/§6, S27's own precedent)."""

  payload: NotRequired[str]
  """Dotted wire key to extract from the raw JSON body before validating it against the
  generated response type (`docs/spec/authoring.md` rule 6) -- e.g. `'positions'` for
  `get_asset_positions`. Absent when the response schema already describes the whole
  body."""


@dataclass(kw_only=True, frozen=True)
class IndexerHttpClient:
  """Shared HTTP transport for the dYdX Indexer's REST API."""

  url: str = INDEXER_HTTP_URL
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  async def __aenter__(self) -> Self:
    """Open the shared HTTP transport."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the shared HTTP transport."""
    await self.http.__aexit__(exc_type, exc_value, traceback)


def _extract(payload: Any, path: str) -> Any:
  """Read a dotted-key path off a decoded JSON body, or return it unread for `''`."""
  if not path:
    return payload
  value = payload
  for part in path.split('.'):
    value = value[part]
  return value


@dataclass(kw_only=True)
class IndexerMixin:
  """Base for every generated Indexer HTTP endpoint module -- the resolved `core` for the
  `indexer/data/` subtree (`codegen/config.toml`)."""

  client: IndexerHttpClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one Indexer REST call (design §2): serialize `request` through
    `request_type`'s validator (ADR 0020/S28) into a plain dict, substitute it into any
    `{placeholder}` in `path` and send the rest as the query string, unwrap
    `meta['payload']` (when declared) from the raw JSON body, and validate the result
    through `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb -- every real Indexer HTTP endpoint is `GET`.
      path: Wire path template, e.g. `/v4/candles/perpetualMarkets/{market}`.
      meta: This call's own quirks -- the wire envelope key to extract, if any
        (`Meta`'s own docstring).
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the extracted value.
    """
    values: dict[str, Any] = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    resolved_path = path
    query: dict[str, Any] = {}
    for key, value in values.items():
      placeholder = f'{{{key}}}'
      if placeholder in resolved_path:
        resolved_path = resolved_path.replace(placeholder, str(value))
      else:
        query[key] = value
    url = path_join(self.client.url, resolved_path)
    response = await self.client.http.request(method, url, params=query or None)
    if response.status_code == 429:
      raise RateLimited(response.status_code, response.json())
    if 400 <= response.status_code < 500:
      raise BadRequest(response.status_code, response.json())
    if response.status_code != 200:
      raise ApiError(response.status_code, response.json())
    should_validate = self.client.validate if validate is None else validate
    payload = _extract(response.json(), meta.get('payload', ''))
    if should_validate and response_type is not None:
      return validator(cast(type, response_type)).python(payload)
    return cast('T', payload)
