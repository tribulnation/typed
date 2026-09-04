"""Wire-value helpers shared by `RpcEndpoint`/`WsRpcEndpoint` -- serializing a generated
`Request` value into a plain, wire-ready dict (ADR 0020/S28), then applying two of
Binance's own wire conventions that design §7 folds into the flat `request` bucket rather
than a per-parameter location marker: a list-typed value is JSON-array-encoded, and `lang`
(the fleet's only declared `in: 'header'` parameter, spot's `yield_arena.activities`) is
routed to a real HTTP header instead of a query/form param.
"""

from typing_extensions import Any, cast
from types import UnionType
import json

from typed_core.validation import validator


def dump_request(request: Any, request_type: type | UnionType | None) -> dict[str, Any] | None:
  """Serialize a generated `Request` value through its own validator (ADR 0020/S28) into
  a plain dict of wire-ready values -- every declared format's serializer (S27) already
  applied -- or `None` for a parameterless call.
  """
  if request_type is None or request is None:
    return None
  return json.loads(validator(cast(type, request_type)).dump(request))


def wire_params(values: dict[str, Any] | None) -> tuple[dict[str, Any] | None, str | None]:
  """Split a serialized request dict into wire `params` and an extracted `lang` header
  value, JSON-array-encoding every list-typed value along the way (Binance's own
  convention for a multi-value parameter, e.g. `symbols=["BTCUSDT","ETHUSDT"]` --
  confirmed by every captured example carrying one).
  """
  if values is None:
    return None, None
  values = dict(values)
  lang = values.pop('lang', None)
  params = {
    key: (json.dumps(value, separators=(',', ':')) if isinstance(value, list) else value)
    for key, value in values.items()
  } if values else None
  return params, lang
