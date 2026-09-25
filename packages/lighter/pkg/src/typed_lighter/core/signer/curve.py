"""ECgFp5 (Pornin): the prime-order group of y^2 = x(x^2 + 2x + 263X) over GF(p^5).

Points use the reference implementation's fractional (x, u) = (X/Z, U/T) coordinates, with
u = x/y. A point encodes to the single GF(p^5) element w = T/U (0 for the neutral element).
Scalars are Python ints modulo the group order `N`.

Two scalar multiplications: `mul` is the reference 5-bit signed fixed window (used by
`schnorr.verify` for e*pk), and `mul_generator` adds one precomputed affine point per 5-bit
digit of the scalar from a per-position table of the generator, with no doublings at all.
The table (64 positions x 16 multiples) is built once, lazily, on first use (~50-200 ms) and
is immutable afterwards.

Ported from poseidon_crypto v0.0.15 (`curve/ecgfp5`). The table is this port's own
addition; it computes the same points as `mul(GENERATOR, s)`.

Nothing here is constant-time: see `typed_lighter.core.signer`.
"""

from typing_extensions import TypeAlias

from . import field
from .field import P, Fp5

N = 1067993516717146951041484916571792702745057740581727230159139685185762082554198619328292418486241
"""Prime order of the group (~2^319)."""

B1 = 263
A: Fp5 = (2, 0, 0, 0, 0)
B_MUL4: Fp5 = (0, 4 * B1, 0, 0, 0)

Point: TypeAlias = tuple[Fp5, Fp5, Fp5, Fp5]
"""(x, z, u, t) with x = X/Z and u = U/T."""
Affine: TypeAlias = tuple[Fp5, Fp5]
"""(x, u), with Z = T = 1."""

NEUTRAL: Point = (field.ZERO, field.ONE, field.ZERO, field.ONE)
GENERATOR: Point = (
  (
    12883135586176881569,
    4356519642755055268,
    5248930565894896907,
    2165973894480315022,
    2448410071095648785,
  ),
  field.ONE,
  field.ONE,
  (4, 0, 0, 0, 0),
)

WINDOW = 5
WINDOW_SIZE = 1 << (WINDOW - 1)
"""Affine multiples per window: 1P .. 16P."""
NUM_DIGITS = (319 + WINDOW) // WINDOW
"""Signed base-32 digits of a scalar (64)."""


def mul_b(a: Fp5, k: int = 1) -> Fp5:
  """a * (k * 263X): multiplication by k times the curve constant b."""
  c = k * B1
  return (3 * c * a[4] % P, c * a[0] % P, c * a[1] % P, c * a[2] % P, c * a[3] % P)


def add(p1: Point, p2: Point) -> Point:
  """Complete addition (reference `ECgFp5Point.Add`)."""
  mul, addf, subf = field.mul, field.add, field.sub
  x1, z1, u1, tt1 = p1
  x2, z2, u2, tt2 = p2
  t1 = mul(x1, x2)
  t2 = mul(z1, z2)
  t3 = mul(u1, u2)
  t4 = mul(tt1, tt2)
  t5 = subf(mul(addf(x1, z1), addf(x2, z2)), addf(t1, t2))
  t6 = subf(mul(addf(u1, tt1), addf(u2, tt2)), addf(t3, t4))
  t7 = addf(t1, mul_b(t2))
  t8 = mul(t4, t7)
  t9 = mul(t3, addf(mul_b(t5, 2), addf(t7, t7)))
  t10 = mul(addf(t4, addf(t3, t3)), addf(t5, t7))
  return (
    mul_b(subf(t10, t8)),
    subf(t8, t9),
    mul(t6, subf(mul_b(t2), t1)),
    addf(t8, t9),
  )


def add_affine(p1: Point, p2: Affine) -> Point:
  """Mixed addition with an affine point (reference `AddAffine`)."""
  mul, addf, subf = field.mul, field.add, field.sub
  x1, z1, u1, tt1 = p1
  x2, u2 = p2
  t1 = mul(x1, x2)
  t3 = mul(u1, u2)
  t5 = addf(x1, mul(x2, z1))
  t6 = addf(u1, mul(u2, tt1))
  t7 = addf(t1, mul_b(z1))
  t8 = mul(tt1, t7)
  t9 = mul(t3, addf(mul_b(t5, 2), addf(t7, t7)))
  t10 = mul(addf(tt1, addf(t3, t3)), addf(t5, t7))
  return (
    mul_b(subf(t10, t8)),
    subf(t8, t9),
    mul(t6, subf(mul_b(z1), t1)),
    addf(t8, t9),
  )


def double(p: Point) -> Point:
  """Point doubling (reference `SetDouble`)."""
  mul, sq, addf, subf = field.mul, field.square, field.add, field.sub
  x, z, u, t = p
  t1 = mul(z, t)
  t2 = mul(t1, t)
  x1 = sq(t2)
  z1 = mul(t1, u)
  t3 = sq(u)
  xz = addf(x, z)
  w1 = subf(t2, mul(t3, addf(xz, xz)))
  t4 = sq(z1)
  z_new = sq(w1)
  return (
    mul_b(t4, 4),
    z_new,
    subf(sq(addf(w1, z1)), addf(t4, z_new)),
    subf(addf(x1, x1), addf(field.scale(t4, 4), z_new)),
  )


def mdouble(p: Point, n: int) -> Point:
  """2^n * p, by the reference's (x, w, z) doubling chain (`SetMDouble`)."""
  if n == 0:
    return p
  if n == 1:
    return double(p)
  mul, sq, addf, subf = field.mul, field.square, field.add, field.sub
  x0, z0, u0, t0 = p
  t1 = mul(z0, t0)
  t2 = mul(t1, t0)
  x1 = sq(t2)
  z1 = mul(t1, u0)
  t3 = sq(u0)
  xz = addf(x0, z0)
  w1 = subf(t2, mul(addf(xz, xz), t3))
  t4 = sq(w1)
  t5 = sq(z1)
  x = mul_b(sq(t5), 16)
  w = subf(addf(x1, x1), addf(field.scale(t5, 4), t4))
  z = subf(sq(addf(w1, z1)), addf(t4, t5))
  b4m4 = subf(B_MUL4, (4, 0, 0, 0, 0))
  for _ in range(2, n):
    t1 = sq(z)
    t2 = sq(t1)
    t3 = sq(w)
    t4 = sq(t3)
    t5 = subf(sq(addf(w, z)), addf(t1, t3))
    xt1 = addf(x, t1)
    z = mul(t5, subf(addf(xt1, xt1), t3))
    x = mul_b(mul(t2, t4), 16)
    w = field.neg(addf(t4, mul(t2, b4m4)))
  t1 = sq(w)
  t2 = sq(z)
  t3 = subf(sq(addf(w, z)), addf(t1, t2))
  xt2 = addf(x, t2)
  w1 = subf(t1, addf(xt2, xt2))
  zf = sq(w1)
  return (
    mul_b(sq(t3)),
    zf,
    mul(t3, w1),
    subf(mul(addf(t1, t1), subf(t1, addf(t2, t2))), zf),
  )


def batch_to_affine(points: list[Point]) -> list[Affine]:
  """(X/Z, U/T) for every point, with a single GF(p^5) inversion (Montgomery's trick)."""
  prefix: list[Fp5] = []
  acc = field.ONE
  for _, z, _, t in points:
    prefix.append(acc)
    acc = field.mul(acc, field.mul(z, t))
  inv_acc = field.inv(acc)
  out: list[Affine] = []
  for i in range(len(points) - 1, -1, -1):
    x, z, u, t = points[i]
    inv_zt = field.mul(inv_acc, prefix[i])
    inv_acc = field.mul(inv_acc, field.mul(z, t))
    out.append((field.mul(field.mul(x, t), inv_zt), field.mul(field.mul(u, z), inv_zt)))
  out.reverse()
  return out


def encode(p: Point) -> Fp5:
  """w = T/U, the canonical one-element encoding (0 for the neutral element)."""
  return field.mul(p[3], field.inv(p[2]))


def decode(w: Fp5) -> Point | None:
  """The point `w` encodes (reference `Decode`), or `None` when it encodes none."""
  e = field.sub(field.square(w), A)
  delta = field.sub(field.square(e), B_MUL4)
  r = field.canonical_sqrt(delta)
  is_square = r is not None
  if r is None:
    r = field.ZERO
  half = field.inv(field.TWO)
  x1 = field.mul(field.add(e, r), half)
  x2 = field.mul(field.sub(e, r), half)
  x = x2 if field.legendre(x1) == 1 else x1
  if is_square:
    return (x, field.ONE, field.ONE, w)
  if w == field.ZERO:
    return NEUTRAL
  return None


def recode_signed(s: int) -> list[int]:
  """Signed base-32 digits of s in [-15, 16], little-endian; the top digit absorbs the carry."""
  digits = []
  mask = (1 << WINDOW) - 1
  half = 1 << (WINDOW - 1)
  carry = 0
  for _ in range(NUM_DIGITS):
    d = (s & mask) + carry
    s >>= WINDOW
    carry = 1 if d > half else 0
    digits.append(d - (carry << WINDOW))
  return digits


def window(p: Point) -> list[Affine]:
  """Affine [1P, 2P, ..., 16P] (reference `MakeWindowAffine`)."""
  tmp = [p]
  for i in range(1, WINDOW_SIZE):
    tmp.append(add(tmp[i - 1], p) if i % 2 == 0 else double(tmp[i >> 1]))
  return batch_to_affine(tmp)


def lookup(win: list[Affine], k: int) -> Affine:
  """k * P from a window, for k in [-16, 16] (k = 0 is never looked up by `mul_generator`)."""
  if k == 0:
    return (field.ZERO, field.ZERO)
  if k > 0:
    return win[k - 1]
  x, u = win[-k - 1]
  return (x, field.neg(u))


def mul(p: Point, s: int) -> Point:
  """s * p, by the reference's signed 5-bit fixed window (`ECgFp5Point.Mul`)."""
  win = window(p)
  digits = recode_signed(s % N)
  x, u = lookup(win, digits[-1])
  r: Point = (x, field.ONE, u, field.ONE)
  for d in reversed(digits[:-1]):
    r = mdouble(r, WINDOW)
    r = add_affine(r, lookup(win, d))
  return r


class GeneratorTable:
  """For every digit position i, the affine window [1..16] * 2^(5i) * G, built on first use."""

  rows: list[list[Affine]] | None = None

  @classmethod
  def get(cls) -> list[list[Affine]]:
    """The table, building it on the first call.

    Two threads racing on the first call both build the same immutable table and one
    assignment wins, so no lock is needed.
    """
    if cls.rows is None:
      points: list[Point] = []
      base = GENERATOR
      for _ in range(NUM_DIGITS):
        tmp = [base]
        for i in range(1, WINDOW_SIZE):
          tmp.append(add(tmp[i - 1], base) if i % 2 == 0 else double(tmp[i >> 1]))
        points.extend(tmp)
        base = mdouble(base, WINDOW)
      flat = batch_to_affine(points)
      cls.rows = [flat[i : i + WINDOW_SIZE] for i in range(0, len(flat), WINDOW_SIZE)]
    return cls.rows


def mul_generator(s: int) -> Point:
  """s * G from the precomputed table: at most 64 mixed additions, no doublings."""
  table = GeneratorTable.get()
  r = NEUTRAL
  for i, d in enumerate(recode_signed(s % N)):
    if d:
      r = add_affine(r, lookup(table[i], d))
  return r
