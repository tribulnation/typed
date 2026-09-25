"""Schnorr signatures over ECgFp5 with a Poseidon2 challenge (poseidon_crypto `signature/schnorr`).

- sign: r = encode(k*G), e = H(r || m) mod n, s = k - e*sk mod n; the signature is s || e,
  80 bytes little-endian.
- verify: r' = encode(s*G + e*pk); accept iff H(r' || m) mod n == e.

The nonce k is hedged (`hedged_nonce`): SHA-512 over a domain tag, the private key, the
message and 32 fresh random bytes, reduced mod n. A broken or repeated RNG (a cloned VM, a
forked process) then still yields a distinct k per (key, message), and a working RNG keeps k
unpredictable even to someone who knows the key and message. Go draws k uniformly from
`crypto/rand` instead; its verifier never sees k, so the two are interchangeable.

Not constant-time: see `typed_lighter.core.signer`.
"""

import hashlib
import os

from . import curve
from . import field
from .curve import N
from .poseidon2 import hash_to_fp5

NONCE_DOMAIN = b'typed-lighter/schnorr-nonce/v1'
"""Domain separation tag of the hedged nonce hash."""


def scalar_from_bytes(b: bytes) -> int:
  """Go `ScalarElementFromLittleEndianBytes`: 40 bytes little-endian, reduced mod n.

  Raises:
    ValueError: `b` is not 40 bytes long.
  """
  if len(b) != 40:
    raise ValueError(f'expected 40 bytes, got {len(b)}')
  return int.from_bytes(b, 'little') % N


def scalar_to_bytes(s: int) -> bytes:
  """A scalar's 40-byte little-endian encoding."""
  return s.to_bytes(40, 'little')


def challenge(*, r: field.Fp5, msg: field.Fp5) -> int:
  """e = the limbs of Poseidon2(r || msg), read as a 320-bit little-endian integer mod n (Go `FromGfp5`)."""
  h = hash_to_fp5([*r, *msg])
  return (h[0] | h[1] << 64 | h[2] << 128 | h[3] << 192 | h[4] << 256) % N


def public_key(sk: int) -> bytes:
  """The 40-byte public key of a private scalar: encode(sk * G)."""
  return field.to_bytes(curve.encode(curve.mul_generator(sk)))


def random_bytes(n: int) -> bytes:
  """`n` bytes from the OS CSPRNG, or none when the platform has no CSPRNG.

  An empty result leaves `hedged_nonce` deterministic (RFC 6979-style: unique per key and
  message), which is still safe: the same message always gets the same signature, and
  different messages different nonces.
  """
  try:
    return os.urandom(n)
  except (NotImplementedError, OSError):
    return b''


def hedged_nonce(sk: int, *, msg_hash: bytes, entropy: bytes) -> int:
  """k = SHA-512(domain || sk || msg_hash || entropy) mod n, never zero.

  The 512-bit digest reduced mod n (~2^319) has a statistical bias below 2^-190.

  Args:
    sk: Private scalar.
    msg_hash: The 40-byte message being signed.
    entropy: Fresh random bytes (32 in normal operation, empty when no CSPRNG exists).
  """
  counter = 0
  while True:
    digest = hashlib.sha512(
      NONCE_DOMAIN
      + scalar_to_bytes(sk)
      + msg_hash
      + entropy
      + counter.to_bytes(4, 'little')
    ).digest()
    k = int.from_bytes(digest, 'little') % N
    if k:
      return k
    counter += 1


def sign(msg_hash: bytes, sk: int, k: int | None = None) -> bytes:
  """Sign a 40-byte, already hashed message; returns the 80-byte signature s || e.

  Args:
    msg_hash: The message hash (a GF(p^5) element, 40 bytes little-endian).
    sk: Private scalar.
    k: Explicit nonce, only for reproducing test vectors; leave `None` for a hedged nonce.
      Reusing a nonce across two messages reveals the private key.

  Raises:
    ValueError: `msg_hash` is not 40 bytes long.
  """
  m = field.from_bytes(msg_hash)
  if k is None:
    k = hedged_nonce(sk, msg_hash=msg_hash, entropy=random_bytes(32))
  r = curve.encode(curve.mul_generator(k))
  e = challenge(r=r, msg=m)
  s = (k - e * sk) % N
  return scalar_to_bytes(s) + scalar_to_bytes(e)


def verify(*, pk: bytes, msg_hash: bytes, sig: bytes) -> bool:
  """Go `schnorr.Validate`: s and e must be canonical (< n), pk must decode, and e must recompute.

  Args:
    pk: The 40-byte public key.
    msg_hash: The 40-byte message hash.
    sig: The 80-byte signature (s || e).
  """
  if len(sig) != 80 or len(pk) != 40 or len(msg_hash) != 40:
    return False
  s = int.from_bytes(sig[:40], 'little')
  e = int.from_bytes(sig[40:], 'little')
  if s >= N or e >= N:
    return False
  point = curve.decode(field.from_bytes(pk))
  if point is None:
    return False
  rv = curve.encode(curve.add(curve.mul_generator(s), curve.mul(point, e)))
  return challenge(r=rv, msg=field.from_bytes(msg_hash)) == e
