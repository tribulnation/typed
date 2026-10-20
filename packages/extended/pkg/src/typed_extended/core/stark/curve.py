"""Stark curve ECDSA, in pure Python: key derivation, deterministic (RFC 6979) signing and
verification, matching `starknet-crypto`'s `ecdsa_sign`/`verify` exactly.

The curve is `y^2 = x^3 + alpha*x + beta` over the Stark prime field, with `alpha = 1`.
Points are kept in Jacobian coordinates while multiplying, so a scalar multiplication costs
a single modular inversion.
"""

from typing_extensions import NamedTuple
import hashlib
import hmac

P = 2**251 + 17 * 2**192 + 1
"""The Stark field prime."""
N = 0x0800000000000010FFFFFFFFFFFFFFFFB781126DCAE7B2321E66A241ADC64D2F
"""The curve order."""
ALPHA = 1
"""Curve coefficient `alpha`."""
BETA = 0x6F21413EFBE40DE150E596D72F7A8C5609AD26C15C915C1F4CDFCB99CEE9E89
"""Curve coefficient `beta`."""
GENERATOR = (
  0x1EF15C18599971B7BECED415A40F0C7DEACFD9B0D1819E03D723D8BC943CFCA,
  0x5668060AA49730B7BE4801DF46EC62DE53ECD11ABE43A32873000C36E8DC1F,
)
"""The generator point, affine `(x, y)`."""
ELEMENT_UPPER_BOUND = 2**251
"""Signature components and message hashes must be below this bound."""


class Signature(NamedTuple):
  """A Stark ECDSA signature."""

  r: int
  """The `x` coordinate of `k * G`."""
  s: int
  """`(msg_hash + r * private_key) / k`, modulo the curve order."""


Jacobian = tuple[int, int, int]
"""A point `(X, Y, Z)` standing for the affine `(X / Z^2, Y / Z^3)`; `Z == 0` is infinity."""

INFINITY: Jacobian = (1, 1, 0)
"""The point at infinity."""


def jacobian_double(p: Jacobian) -> Jacobian:
  """Double a Jacobian point."""
  x, y, z = p
  if z == 0 or y == 0:
    return INFINITY
  yy = y * y % P
  s = 4 * x * yy % P
  zz = z * z % P
  m = (3 * x * x + ALPHA * zz * zz) % P
  nx = (m * m - 2 * s) % P
  ny = (m * (s - nx) - 8 * yy * yy) % P
  nz = 2 * y * z % P
  return nx, ny, nz


def jacobian_add(p: Jacobian, q: Jacobian) -> Jacobian:
  """Add two Jacobian points."""
  if p[2] == 0:
    return q
  if q[2] == 0:
    return p
  x1, y1, z1 = p
  x2, y2, z2 = q
  z1z1 = z1 * z1 % P
  z2z2 = z2 * z2 % P
  u1 = x1 * z2z2 % P
  u2 = x2 * z1z1 % P
  s1 = y1 * z2 * z2z2 % P
  s2 = y2 * z1 * z1z1 % P
  if u1 == u2:
    return jacobian_double(p) if s1 == s2 else INFINITY
  h = (u2 - u1) % P
  hh = h * h % P
  hhh = h * hh % P
  r = (s2 - s1) % P
  v = u1 * hh % P
  nx = (r * r - hhh - 2 * v) % P
  ny = (r * (v - nx) - s1 * hhh) % P
  nz = z1 * z2 * h % P
  return nx, ny, nz


def to_affine(p: Jacobian) -> tuple[int, int] | None:
  """Convert a Jacobian point to affine `(x, y)`, or `None` for infinity."""
  x, y, z = p
  if z == 0:
    return None
  zinv = pow(z, -1, P)
  zinv2 = zinv * zinv % P
  return x * zinv2 % P, y * zinv2 * zinv % P


def multiply(k: int, point: tuple[int, int]) -> tuple[int, int] | None:
  """Multiply an affine point by a scalar, returning the affine result (`None` for infinity)."""
  result = INFINITY
  addend: Jacobian = (point[0], point[1], 1)
  while k:
    if k & 1:
      result = jacobian_add(result, addend)
    addend = jacobian_double(addend)
    k >>= 1
  return to_affine(result)


def public_key(private_key: int) -> int:
  """The Stark public key of a private key: the `x` coordinate of `private_key * G`.

  Raises:
    ValueError: The private key is outside `[1, N)`.
  """
  if not 0 < private_key < N:
    raise ValueError('Stark private key must be in [1, N)')
  point = multiply(private_key, GENERATOR)
  assert point is not None
  return point[0]


def generate_k(msg_hash: int, private_key: int, seed: int | None = None) -> int:
  """Deterministic nonce per RFC 6979 (HMAC-SHA256 DRBG), as `starknet-crypto` derives it.

  The 32-byte private key is the entropy input, the 32-byte message hash the nonce, and the
  seed (leading zero bytes stripped; empty when absent) the personalization string. Each
  candidate is the DRBG's 32-byte output shifted right by 4 bits, accepted when in `[1, N)`.

  Args:
    msg_hash: The message hash being signed.
    private_key: The signing key.
    seed: Retry counter: `None` first, then 1, 2, ... after an unusable `k`.
  """
  x = private_key.to_bytes(32, 'big')
  h = msg_hash.to_bytes(32, 'big')
  data = b'' if seed is None else seed.to_bytes(32, 'big').lstrip(b'\x00')
  key = b'\x00' * 32
  v = b'\x01' * 32
  key = hmac.new(key, v + b'\x00' + x + h + data, hashlib.sha256).digest()
  v = hmac.new(key, v, hashlib.sha256).digest()
  key = hmac.new(key, v + b'\x01' + x + h + data, hashlib.sha256).digest()
  v = hmac.new(key, v, hashlib.sha256).digest()
  while True:
    v = hmac.new(key, v, hashlib.sha256).digest()
    k = int.from_bytes(v, 'big') >> 4
    if 0 < k < N:
      return k
    key = hmac.new(key, v + b'\x00', hashlib.sha256).digest()
    v = hmac.new(key, v, hashlib.sha256).digest()


def sign(private_key: int, msg_hash: int) -> Signature:
  """Sign a message hash, deterministically: the same key and hash always give the same
  signature, identical to `starknet-crypto`'s `ecdsa_sign`.

  Raises:
    ValueError: The message hash is not below `2^251`.
  """
  if not 0 <= msg_hash < ELEMENT_UPPER_BOUND:
    raise ValueError('Message hash must be below 2^251')
  seed: int | None = None
  while True:
    k = generate_k(msg_hash, private_key, seed)
    seed = 1 if seed is None else seed + 1
    point = multiply(k, GENERATOR)
    if point is None:
      continue
    r = point[0]
    if not 0 < r < ELEMENT_UPPER_BOUND:
      continue
    s = (msg_hash + r * private_key) * pow(k, -1, N) % N
    if not 0 < s < ELEMENT_UPPER_BOUND:
      continue
    return Signature(r, s)


def sqrt_mod(value: int) -> int | None:
  """A square root modulo `P` (Tonelli-Shanks), or `None` when `value` is not a square."""
  value %= P
  if value == 0:
    return 0
  if pow(value, (P - 1) // 2, P) != 1:
    return None
  q, s = P - 1, 0
  while q % 2 == 0:
    q //= 2
    s += 1
  z = 2
  while pow(z, (P - 1) // 2, P) != P - 1:
    z += 1
  m, c, t, root = s, pow(z, q, P), pow(value, q, P), pow(value, (q + 1) // 2, P)
  while t != 1:
    i, t2 = 0, t
    while t2 != 1:
      t2 = t2 * t2 % P
      i += 1
    b = pow(c, 1 << (m - i - 1), P)
    m, c = i, b * b % P
    t, root = t * c % P, root * b % P
  return root


def verify(public_key: int, msg_hash: int, signature: Signature) -> bool:
  """Check a signature against a public key (an `x` coordinate; either `y` is accepted)."""
  r, s = signature
  if not (
    0 < r < ELEMENT_UPPER_BOUND and 0 < s < N and 0 <= msg_hash < ELEMENT_UPPER_BOUND
  ):
    return False
  y = sqrt_mod(public_key**3 + ALPHA * public_key + BETA)
  if y is None:
    return False
  w = pow(s, -1, N)
  zg = multiply(msg_hash * w % N, GENERATOR)
  for candidate in (y, P - y):
    rq = multiply(r * w % N, (public_key, candidate))
    total = jacobian_add(
      INFINITY if zg is None else (zg[0], zg[1], 1),
      INFINITY if rq is None else (rq[0], rq[1], 1),
    )
    point = to_affine(total)
    if point is not None and point[0] == r:
      return True
  return False
