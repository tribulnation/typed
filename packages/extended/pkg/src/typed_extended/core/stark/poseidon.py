"""Starknet's Poseidon hash, in pure Python: the Hades permutation over the Stark field
(width 3, 8 full and 83 partial rounds, cube S-box), and `poseidon_hash_many`'s sponge.
"""

from typing_extensions import Iterable
import hashlib

from .curve import P

FULL_ROUNDS = 8
"""Full rounds, split evenly before and after the partial rounds."""
PARTIAL_ROUNDS = 83
"""Partial rounds (S-box on the last state element only)."""


def round_constant(n: int) -> int:
  """The `n`-th round constant: `sha256("Hades{n}") mod P`."""
  return int(hashlib.sha256(f'Hades{n}'.encode()).hexdigest(), 16) % P


ROUND_CONSTANTS: list[tuple[int, int, int]] = [
  (round_constant(3 * i), round_constant(3 * i + 1), round_constant(3 * i + 2))
  for i in range(FULL_ROUNDS + PARTIAL_ROUNDS)
]
"""Per-round constants, three per round."""


def permute(state: tuple[int, int, int]) -> tuple[int, int, int]:
  """Apply the Hades permutation to a 3-element state."""
  a, b, c = state
  half = FULL_ROUNDS // 2
  for index, (k0, k1, k2) in enumerate(ROUND_CONSTANTS):
    a, b, c = (a + k0) % P, (b + k1) % P, (c + k2) % P
    if index < half or index >= half + PARTIAL_ROUNDS:
      a, b, c = pow(a, 3, P), pow(b, 3, P), pow(c, 3, P)
    else:
      c = pow(c, 3, P)
    # MDS matrix [[3, 1, 1], [1, -1, 1], [1, 1, -2]]
    a, b, c = (3 * a + b + c) % P, (a - b + c) % P, (a + b - 2 * c) % P
  return a, b, c


def poseidon_hash_many(values: Iterable[int]) -> int:
  """Hash a sequence of field elements: absorb pairs into a width-3 sponge after padding
  with a single `1` (and a `0` when that leaves an odd count), then squeeze one element.
  """
  items = [value % P for value in values]
  items.append(1)
  if len(items) % 2:
    items.append(0)
  state = (0, 0, 0)
  for i in range(0, len(items), 2):
    state = permute(
      ((state[0] + items[i]) % P, (state[1] + items[i + 1]) % P, state[2])
    )
  return state[0]
