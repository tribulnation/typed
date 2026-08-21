"""Etherscan's response envelope.

Most endpoints wrap their payload as `{status, message, result}`; `proxy.*` endpoints
return a JSON-RPC-shaped `{jsonrpc, id, result | error}` frame instead. Both are kept
whole rather than unwrapped to `result` (`docs/spec/authoring.md` rule 6): `status`
genuinely means different things on different endpoints -- a live capture of
`account.token1155tx`'s second page is honestly `status='0'`, `message='No records
found'`, `result=[]`, not an error, while another endpoint's `status='0'` is a real
failure. Nothing here can tell those apart from `status`/`message` alone, so the two
signals below -- a rate limit and a rejected API key, unambiguous regardless of endpoint
-- are the only ones raised on; everything else is handed back whole for the caller (or a
generated method's own declared response type) to interpret.
"""

from typing_extensions import Any
import httpx

from typed_core.exceptions import AuthError, RateLimited


def _signal(data: Any) -> str:
  """Return the string most likely to carry an error message, or `''`.

  Checked in the order a real failure actually shows up: a non-JSON-RPC error puts its
  message in `result` (the field a caller would otherwise treat as the payload); a
  JSON-RPC error puts it in `error.message`; failing both, `message` is a last resort.
  """
  if not isinstance(data, dict):
    return ''
  result = data.get('result')
  if isinstance(result, str):
    return result
  error = data.get('error')
  if isinstance(error, dict) and isinstance(error.get('message'), str):
    return error['message']
  message = data.get('message')
  return message if isinstance(message, str) else ''


def unwrap(response: httpx.Response) -> Any:
  """Parse the response body and raise on the two signals every endpoint agrees on.

  Everything else -- success, or a per-endpoint-specific error message -- is returned
  whole; the generated method's own declared response type is what interprets it further.
  """
  data = response.json()
  signal = _signal(data).lower()
  if 'rate limit' in signal:
    raise RateLimited(data)
  if 'invalid api key' in signal or 'missing api key' in signal:
    raise AuthError(data)
  return data
