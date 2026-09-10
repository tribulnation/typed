"""Bit2Me exceptions: a re-export of the shared `typed-core` hierarchy plus the
HTTP-status/WS-close-code mapping documented in `spec/core.md`'s Errors table.

Bit2Me's error signal is HTTP status alone on the `http` surface (error bodies vary
enough in shape across endpoints — sometimes `errorPayload`, sometimes a nested
`data: {errorCode, errorType}` — that nothing but the status code is a reliable
discriminator) and WS close codes on `trading_ws`/`crypto_ws`/`explorer_ws`. Neither
needs a venue-specific exception subclass; every signal maps onto a shared one.

The one error body worth reading is the wallet proforma's `412 not-enough-funds`: it is
the only place Bit2Me publishes the withdrawal fee it would charge, so `ProformaShortfall`
types it and `not_enough_funds` reads it off a caught `ApiError`.
"""

from decimal import Decimal
from typing_extensions import Any, Literal, NotRequired
import httpx

from typed_core.validation import validator, TypedDict as CoreTypedDict
from typed_core.exceptions import (
  Error,
  NetworkError,
  ValidationError,
  ApiError,
  BadRequest,
  AuthError,
  RateLimited,
  LogicError,
)

__all__ = [
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
  'raise_http_status',
  'ProformaShortfall',
  'not_enough_funds',
]


def raise_http_status(response: httpx.Response):
  """Raise the `typed_core` exception matching a non-2xx HTTP response, per
  `spec/core.md`'s Errors table.

  Args:
    response: The failed response. Its body is decoded as JSON when possible, since
      Bit2Me's error payloads usually are, falling back to raw text otherwise.
  """
  payload: Any
  try:
    payload = response.json()
  except Exception:
    payload = response.text
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  elif status == 400:
    raise BadRequest(status, payload)
  elif status in (429, 418):
    raise RateLimited(status, payload)
  else:
    raise ApiError(status, payload)


class ProformaShortfall(CoreTypedDict):
  """The `412 not-enough-funds` body `POST /v1/wallet/transaction/proforma` answers when the
  source pocket can't cover the requested amount.

  Undocumented upstream. Confirmed live on blockchain-withdrawal proformas for BTC, ETH,
  USDT and SOL from an under-funded pocket, every one carrying all five fields. Only
  `code` and `fee` are required here: the helper exists for the fee, so it refuses a body
  over the two fields it is for and not over the request echo around them.
  """

  code: Literal['not-enough-funds']
  fee: Decimal
  """Withdrawal fee Bit2Me would charge, in `currency`. A decimal string on the wire, e.g.
  `'0.00020000'` for ETH on Ethereum; `'0.00000000'` when the venue charges none."""
  amount: NotRequired[Decimal]
  """The requested amount, echoed back as a decimal string."""
  currency: NotRequired[str]
  """The requested asset, which `fee`, `amount` and `minimumAmount` are denominated in."""
  minimumAmount: NotRequired[float]
  """Smallest withdrawable amount of `currency`. A JSON number on the wire, unlike `fee`
  and `amount`, so it can't be read as `Decimal` without inventing precision."""


def not_enough_funds(error: ApiError) -> ProformaShortfall | None:
  """Read the `not-enough-funds` body off a failed wallet proforma, which is the only
  place Bit2Me publishes a withdrawal fee.

  Bit2Me nests the body twice: `ApiError.args[1]` is the `412` envelope, its `data` repeats
  the envelope, and that one's `data` is the `ProformaShortfall`.

  Args:
    error: The exception raised by `v1.wallet.transactions.preview`.

  Returns:
    The validated shortfall body, or `None` when `error` is not a `412`, its body doesn't
    carry the nested `data.data` envelope, or that carries another `code` or no `fee`.

  Examples:
    ```python
    from typed_bit2me import Bit2Me
    from typed_bit2me.core.exc import ApiError, not_enough_funds

    async with Bit2Me.new() as client:
      try:
        await client.v1.wallet.transactions.preview(
          amount='0.01',
          currency='ETH',
          destination={'address': '0x...', 'network': 'ethereum'},
        )
      except ApiError as e:
        shortfall = not_enough_funds(e)
        if shortfall is None:
          raise
        print(shortfall['fee'])  # Decimal('0.00020000')
    ```
  """
  if len(error.args) < 2 or error.args[0] != 412:
    return None
  envelope = error.args[1]
  if not isinstance(envelope, dict):
    return None
  inner = envelope.get('data')
  if not isinstance(inner, dict):
    return None
  try:
    return validator(ProformaShortfall)(inner.get('data'))
  except ValidationError:
    return None
