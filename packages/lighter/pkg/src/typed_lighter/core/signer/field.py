"""The Goldilocks field GF(p), p = 2^64 - 2^32 + 1, and its quintic extension GF(p^5) = GF(p)[X]/(X^5 - 3).

Base-field elements are plain `int`s in `[0, p)`. Extension elements are 5-tuples of
base-field elements, lowest degree first. Every function returns canonical (fully reduced)
values: products are accumulated as Python big ints and reduced once per output limb.

Ported from poseidon_crypto v0.0.15 (`field/goldilocks`, `field/goldilocks_quintic_extension`).
"""

from typing_extensions import TypeAlias

P = 0xFFFFFFFF00000001
"""The Goldilocks prime."""
MASK64 = (1 << 64) - 1
DTH_ROOT = 1041288259238279555
"""A primitive 5th root of unity in GF(p); drives the Frobenius map."""
TWO_ADICITY = 32
POWER_OF_TWO_GENERATOR = 7277203076849721926
"""A generator of GF(p)'s 2^32-order multiplicative subgroup (Tonelli-Shanks)."""

Fp5: TypeAlias = tuple[int, int, int, int, int]
"""A GF(p^5) element, lowest degree first."""

ZERO: Fp5 = (0, 0, 0, 0, 0)
ONE: Fp5 = (1, 0, 0, 0, 0)
TWO: Fp5 = (2, 0, 0, 0, 0)

FROBENIUS = tuple(tuple(pow(DTH_ROOT, c * i, P) for i in range(5)) for c in range(5))
"""`FROBENIUS[c][i]` = DTH_ROOT^(c*i): the coefficient twists of `a^(p^c)`."""


def from_go_int(x: int) -> int:
  """A Go integer's value as a Goldilocks element, the way `GoldilocksField(x)` casts it.

  Go converts any integer type to the field's `uint64` by two's complement, so a negative
  `int64` (or a sign-extended `int16`) wraps to `2^64 + x` first and is only then reduced
  mod p: `-1` maps to `2^32 - 2`, not to `p - 1`.
  """
  return (x & MASK64) % P


def f_inv(a: int) -> int:
  """Inverse in GF(p), or 0 for 0 (Go's `InverseOrZero`)."""
  return pow(a, P - 2, P)


def f_sqrt(a: int) -> int | None:
  """A square root in GF(p) by Tonelli-Shanks (poseidon_crypto `SqrtF`), or `None`."""
  if a == 0:
    return 0
  if pow(a, (P - 1) >> 1, P) != 1:
    return None
  t = (P - 1) >> TWO_ADICITY
  z = POWER_OF_TWO_GENERATOR
  w = pow(a, (t - 1) >> 1, P)
  x = a * w % P
  b = x * w % P
  v = TWO_ADICITY
  while b != 1:
    k = 0
    b2k = b
    while b2k != 1:
      b2k = b2k * b2k % P
      k += 1
    w = z
    for _ in range(v - k - 1):
      w = w * w % P
    z = w * w % P
    b = b * z % P
    x = x * w % P
    v = k
  return x


def add(a: Fp5, b: Fp5) -> Fp5:
  """a + b."""
  return (
    (a[0] + b[0]) % P,
    (a[1] + b[1]) % P,
    (a[2] + b[2]) % P,
    (a[3] + b[3]) % P,
    (a[4] + b[4]) % P,
  )


def sub(a: Fp5, b: Fp5) -> Fp5:
  """a - b."""
  return (
    (a[0] - b[0]) % P,
    (a[1] - b[1]) % P,
    (a[2] - b[2]) % P,
    (a[3] - b[3]) % P,
    (a[4] - b[4]) % P,
  )


def neg(a: Fp5) -> Fp5:
  """-a."""
  return (-a[0] % P, -a[1] % P, -a[2] % P, -a[3] % P, -a[4] % P)


def scale(a: Fp5, s: int) -> Fp5:
  """a * s, for a base-field scalar s."""
  return (a[0] * s % P, a[1] * s % P, a[2] * s % P, a[3] * s % P, a[4] * s % P)


def mul(a: Fp5, b: Fp5) -> Fp5:
  """a * b (schoolbook, one reduction per limb; X^5 = 3)."""
  a0, a1, a2, a3, a4 = a
  b0, b1, b2, b3, b4 = b
  return (
    (a0 * b0 + 3 * (a1 * b4 + a2 * b3 + a3 * b2 + a4 * b1)) % P,
    (a0 * b1 + a1 * b0 + 3 * (a2 * b4 + a3 * b3 + a4 * b2)) % P,
    (a0 * b2 + a1 * b1 + a2 * b0 + 3 * (a3 * b4 + a4 * b3)) % P,
    (a0 * b3 + a1 * b2 + a2 * b1 + a3 * b0 + 3 * a4 * b4) % P,
    (a0 * b4 + a1 * b3 + a2 * b2 + a3 * b1 + a4 * b0) % P,
  )


def square(a: Fp5) -> Fp5:
  """a^2."""
  a0, a1, a2, a3, a4 = a
  return (
    (a0 * a0 + 6 * (a1 * a4 + a2 * a3)) % P,
    (2 * a0 * a1 + 6 * a2 * a4 + 3 * a3 * a3) % P,
    (2 * a0 * a2 + a1 * a1 + 6 * a3 * a4) % P,
    (2 * (a0 * a3 + a1 * a2) + 3 * a4 * a4) % P,
    (2 * (a0 * a4 + a1 * a3) + a2 * a2) % P,
  )


def frobenius(a: Fp5, count: int = 1) -> Fp5:
  """a^(p^count)."""
  z = FROBENIUS[count % 5]
  return (a[0], a[1] * z[1] % P, a[2] * z[2] % P, a[3] * z[3] % P, a[4] * z[4] % P)


def norm_limb0(a: Fp5, f: Fp5) -> int:
  """Limb 0 of a * f, the only limb of a norm product that is ever needed."""
  return (a[0] * f[0] + 3 * (a[1] * f[4] + a[2] * f[3] + a[3] * f[2] + a[4] * f[1])) % P


def inv(a: Fp5) -> Fp5:
  """a^-1, or zero for zero (Go's `InverseOrZero`), via the norm: a^-1 = a^(r-1) / N(a)."""
  d = frobenius(a)
  e = mul(d, frobenius(d))
  f = mul(e, frobenius(e, 2))
  return scale(f, f_inv(norm_limb0(a, f)))


def legendre(a: Fp5) -> int:
  """Legendre symbol of a, as a base-field value: 0, 1 or p - 1."""
  f1 = frobenius(a)
  f2 = frobenius(f1)
  f12 = mul(f1, f2)
  norm = mul(mul(a, f12), frobenius(f12, 2))[0]
  return pow(norm, (P - 1) >> 1, P)


def sqrt(a: Fp5) -> Fp5 | None:
  """Some square root of a (poseidon_crypto `Sqrt`), or `None` when a is not a square."""
  v = a
  for _ in range(31):
    v = square(v)
  v32 = v
  for _ in range(32):
    v32 = square(v32)
  d = mul(mul(a, v32), inv(v))
  e = frobenius(mul(d, frobenius(d, 2)))
  s = f_sqrt(norm_limb0(a, square(e)))
  if s is None:
    return None
  return scale(inv(e), s)


def canonical_sqrt(a: Fp5) -> Fp5 | None:
  """A square root with poseidon_crypto's `Sgn0` convention: negated when limb 0 is even."""
  r = sqrt(a)
  if r is None:
    return None
  return neg(r) if r[0] % 2 == 0 else r


def to_bytes(a: Fp5) -> bytes:
  """The 40-byte little-endian encoding."""
  return b''.join(x.to_bytes(8, 'little') for x in a)


def from_bytes(b: bytes) -> Fp5:
  """Decode 40 little-endian bytes.

  Limbs >= p are reduced rather than rejected, as Go's `FromCanonicalLittleEndianBytes`
  (which never range-checks) effectively does: its verifier accepts such encodings too.

  Raises:
    ValueError: `b` is not 40 bytes long.
  """
  if len(b) != 40:
    raise ValueError(f'expected 40 bytes, got {len(b)}')
  limbs = [int.from_bytes(b[i : i + 8], 'little') % P for i in range(0, 40, 8)]
  return (limbs[0], limbs[1], limbs[2], limbs[3], limbs[4])
