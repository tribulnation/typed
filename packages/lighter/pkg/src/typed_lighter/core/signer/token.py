"""Standard auth tokens: `{deadline}:{account_index}:{api_key_index}:{signature_hex}`.

lighter-go `types.ConstructAuthToken`: the message is the first three segments; its UTF-8
bytes are read as 8-byte little-endian field elements (the last one zero-padded), hashed with
Poseidon2 to a GF(p^5) element, and Schnorr-signed. The signature is appended as lowercase
hex. The venue's docs call that last segment "random hex"; it is the signature.
"""

from datetime import datetime

from ..exc import BadRequest
from ..types import timestamp_seconds
from . import field
from . import schnorr
from .poseidon2 import bytes_to_elements, hash_to_fp5
from .txs.base import MessageSigner


def auth_message_hash(message: str) -> bytes:
  """The 40-byte hash an auth token's signature covers."""
  return field.to_bytes(hash_to_fp5(bytes_to_elements(message.encode())))


def aware(value: datetime, name: str) -> datetime:
  """`value`, checked to be timezone-aware.

  A signed time is committed to by the signature, so a naive `datetime` (which Python would
  read as local time) is refused rather than guessed at.

  Raises:
    BadRequest: `value` is naive.
  """
  if value.tzinfo is None or value.utcoffset() is None:
    raise BadRequest(
      f'{name} must be a timezone-aware datetime, e.g. datetime.now(timezone.utc); '
      f'got the naive {value.isoformat()}'
    )
  return value


def auth_token(
  signer: MessageSigner, *, deadline: datetime, account_index: int, api_key_index: int
) -> str:
  """Build a standard auth token.

  Args:
    signer: The API key of `api_key_index`.
    deadline: Expiry, sent in whole epoch seconds. Lighter rejects a token whose expiry is
      more than 8 hours ahead at the time of the request.
    account_index: Account the token authenticates.
    api_key_index: Slot of the signing key.

  Raises:
    BadRequest: `deadline` is naive.
  """
  deadline = aware(deadline, 'deadline')
  return sign_auth_message(
    signer, f'{timestamp_seconds.dump(deadline)}:{account_index}:{api_key_index}'
  )


def sign_auth_message(signer: MessageSigner, message: str) -> str:
  """Append the signature of an auth token's `{deadline}:{account_index}:{api_key_index}`
  message to it, with no check on the values it holds.

  Args:
    signer: The API key named in `message`.
    message: The token's first three segments.
  """
  return f'{message}:{signer.sign(auth_message_hash(message)).hex()}'


def verify_auth_token(token: str, public_key: bytes) -> bool:
  """Whether a standard auth token's signature is valid for `public_key`."""
  message, _, signature = token.rpartition(':')
  try:
    sig = bytes.fromhex(signature)
  except ValueError:
    return False
  return schnorr.verify(pk=public_key, msg_hash=auth_message_hash(message), sig=sig)
