"""Wire-value helpers shared by `RpcEndpoint`/`PublicStreamEndpoint`/`PrivateStreamEndpoint`:
substituting a `path`/`channel` template's `{placeholder}` segments from a generated
`Request`/`Parameters` value's own serialized fields (design §7 -- "derived from the
template string itself", not a spec-declared role marker). Every generated call passes
its `path`/`channel` as a bare, un-interpolated string (kucoin's own `futures.orders.
get_by_order_id` renders `path='/api/v1/orders/{order-id}'`, never an f-string) -- `core`
is exactly where that substitution belongs, the identical convention every other wire
decision (query-vs-body, header routing) already lives at.
"""

from typing_extensions import Any
import re

PLACEHOLDER = re.compile(r'\{([^{}]+)\}')


def substitute_template(template: str, values: dict[str, Any] | None) -> tuple[str, dict[str, Any] | None]:
  """Fill every `{name}` segment of `template` from `values`, returning the substituted
  string and the remaining values with each consumed key removed -- a path/channel
  parameter is never also sent as a query/body field or a channel-adjacent value.

  Args:
    template: A `path`/`channel` string, with zero or more `{name}` placeholders.
    values: The generated call's own serialized `Request`/`Parameters` dict, or `None`
      for a parameterless operation (never reached if `template` carries a placeholder --
      a spec whose path/channel is templated always declares a matching request field).
  """
  names = PLACEHOLDER.findall(template)
  if not names:
    return template, values
  remaining = dict(values) if values is not None else {}
  filled = template
  for name in names:
    filled = filled.replace('{' + name + '}', str(remaining.pop(name)))
  return filled, (remaining or None)
