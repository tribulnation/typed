"""Client-side state for RISEx's anchor + bitmap nonces.

Every account-scoped signature (permits, signer registration, allowances) consumes one
`(nonceAnchor, nonceBitmap)` pair, each usable once. The contract accepts the account's
current anchor or the next one, so the client starts each session on a fresh anchor
(`nonce_anchor + 1` from `GET /v1/nonce-state/{account}`, bit 0): nothing it signs can
collide with a permit already in flight from another process. Bits are handed out in
order; after bit 207 the next anchor starts at bit 0. Gaps are harmless, so a signature
that is never submitted, or that reverts, costs nothing but its bit.
"""

from typing_extensions import Awaitable, Callable
from dataclasses import dataclass, field
import asyncio

from .eip712 import MAX_NONCE_BIT


@dataclass
class Nonces:
  """Hands out `(anchor, bit)` pairs for one account, safely across concurrent callers."""

  anchor: int | None = None
  """Anchor being consumed; `None` until loaded, or after `reset`."""
  bit: int = 0
  """Next bit of `anchor` to hand out."""
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def take(self, load: Callable[[], Awaitable[int]]) -> tuple[int, int]:
    """The next unused `(anchor, bit)` pair.

    Args:
      load: Fetches the account's current on-chain anchor; called on first use and
        after `reset`.
    """
    async with self.lock:
      if self.anchor is None:
        self.anchor, self.bit = await load() + 1, 0
      elif self.bit > MAX_NONCE_BIT:
        self.anchor, self.bit = self.anchor + 1, 0
      pair = self.anchor, self.bit
      self.bit += 1
      return pair

  def reset(self):
    """Forget the state, so the next `take` reloads it: after the venue rejected a
    signature's nonce (another process moved the anchor, say).
    """
    self.anchor = None
    self.bit = 0
