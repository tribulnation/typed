"""Poseidon2 over Goldilocks: width 12, rate 8, x^7 S-box, 8 full and 22 partial rounds.

This one permutation serves both poseidon_crypto packages lighter-go uses:
`poseidon2_goldilocks_plonky2` (transaction hashes, the Schnorr challenge) and
`poseidon2_goldilocks` (auth-token messages). They share constants and compute the same
permutation.

The sponge overwrites instead of adding and applies no padding (`HashNToMNoPad`), so it is
length-ambiguous: H(x) = H(x || 0) whenever the zeros stay inside the same rate block.
Harmless for Lighter's fixed transaction layouts, and reproduced exactly.
"""

from .field import MASK64, P, Fp5
from .poseidon2_constants import EXTERNAL_CONSTANTS, INTERNAL_CONSTANTS, MATRIX_DIAG

WIDTH = 12
RATE = 8

HashOut = tuple[int, int, int, int]
"""A 4-element Plonky2 hash output (`poseidon2_goldilocks_plonky2.HashOut`)."""


def external_layer(s: list[int]) -> list[int]:
  """External linear layer: circ(2*M4, M4, M4), M4 the Plonky3 4x4 MDS matrix, reduced mod p."""
  out = [0] * WIDTH
  for i in range(0, WIDTH, 4):
    x0, x1, x2, x3 = s[i], s[i + 1], s[i + 2], s[i + 3]
    t01 = x0 + x1
    t23 = x2 + x3
    t = t01 + t23
    out[i] = t + t01 + x1
    out[i + 1] = t + x1 + 2 * x2
    out[i + 2] = t + t23 + x3
    out[i + 3] = t + x3 + 2 * x0
  s0 = out[0] + out[4] + out[8]
  s1 = out[1] + out[5] + out[9]
  s2 = out[2] + out[6] + out[10]
  s3 = out[3] + out[7] + out[11]
  return [
    (out[0] + s0) % P,
    (out[1] + s1) % P,
    (out[2] + s2) % P,
    (out[3] + s3) % P,
    (out[4] + s0) % P,
    (out[5] + s1) % P,
    (out[6] + s2) % P,
    (out[7] + s3) % P,
    (out[8] + s0) % P,
    (out[9] + s1) % P,
    (out[10] + s2) % P,
    (out[11] + s3) % P,
  ]


def permute(state: list[int]) -> list[int]:
  """The Poseidon2 permutation of 12 canonical field elements."""
  s = external_layer(state)
  for r in range(4):
    rc = EXTERNAL_CONSTANTS[r]
    s = external_layer([pow(s[i] + rc[i], 7, P) for i in range(WIDTH)])
  diag = MATRIX_DIAG
  for rc in INTERNAL_CONSTANTS:
    s[0] = pow(s[0] + rc, 7, P)
    total = sum(s)
    s = [(total + s[i] * diag[i]) % P for i in range(WIDTH)]
  for r in range(4, 8):
    rc = EXTERNAL_CONSTANTS[r]
    s = external_layer([pow(s[i] + rc[i], 7, P) for i in range(WIDTH)])
  return s


def hash_n_to_m_no_pad(inputs: list[int], num_outputs: int) -> list[int]:
  """Go `HashNToMNoPad`: overwrite-mode sponge, no padding.

  Inputs are raw Go `uint64` field values and are reduced mod p on absorption, which is
  what Go's arithmetic does with a non-canonical element.
  """
  state = [0] * WIDTH
  for i in range(0, len(inputs), RATE):
    for j, x in enumerate(inputs[i : i + RATE]):
      state[j] = (x & MASK64) % P
    state = permute(state)
  out: list[int] = []
  while True:
    for i in range(RATE):
      out.append(state[i])
      if len(out) == num_outputs:
        return out
    state = permute(state)


def hash_to_fp5(inputs: list[int]) -> Fp5:
  """Go `HashToQuinticExtension`: the first five squeezed elements, as a GF(p^5) element."""
  h = hash_n_to_m_no_pad(inputs, 5)
  return (h[0], h[1], h[2], h[3], h[4])


def hash_no_pad(inputs: list[int]) -> HashOut:
  """Go `HashNoPad`: the first four squeezed elements."""
  h = hash_n_to_m_no_pad(inputs, 4)
  return (h[0], h[1], h[2], h[3])


def hash_two_to_one(a: HashOut, b: HashOut) -> HashOut:
  """Go `HashTwoToOne`: `HashNoPad(a || b)`."""
  return hash_no_pad([*a, *b])


def bytes_to_elements(data: bytes) -> list[int]:
  """Go `ArrayFromCanonicalLittleEndianBytes`: 8-byte little-endian chunks, the last one zero-padded.

  Raises:
    ValueError: A chunk is >= p (impossible for ASCII text, whose bytes are all < 0x80).
  """
  out = []
  for i in range(0, len(data), 8):
    x = int.from_bytes(data[i : i + 8].ljust(8, b'\0'), 'little')
    if x >= P:
      raise ValueError('non-canonical field element in byte string')
    out.append(x)
  return out
