"""Per-API-key nonce management for `client.tx`.

Each API key has its own nonce, which goes up by exactly one per transaction unless the
transaction is signed with `skip_nonce` (a `client.signer` option: any increasing nonce is
then accepted, and a pre-signed one sent with `tx.send`/`tx.batch` moves the cache past it
like any pinned nonce). `NonceManager` always hands out the exact next nonce: it caches it
per key (fetched from `GET /api/v1/nextNonce` on first use), rotates round-robin across the
configured keys, and holds a per-key lock from signing through submission, so one key's
transactions reach the sequencer in nonce order. A batch holds `count` consecutive nonces
under the same lock and settles them together.

After a submission:

- accepted (`code` 200): the nonce is consumed, even if the sequencer later rejects the
  transaction, so the cached value moves on by one (by `count` for a batch);
- refused with a business code other than `21104` (a `BadRequest`, `AuthError` or
  `RateLimited` carrying a code, see `core.envelope.error_code`): the API layer refused it
  before the sequencer saw it, so the nonce was not consumed and is reused;
- anything else (`21104 invalid nonce`, any HTTP 5xx even with a business code in its body,
  a code-less HTTP status error or WebSocket error frame, an unclassified code, a network
  error, a timeout, a cancellation): the transaction may have landed, or the nonce is out
  of sync, so the cache is dropped and refetched next time.

A transaction signed with a caller-pinned nonce (`tx.*(nonce=...)`, or a pre-signed one
submitted with `tx.send`/`tx.batch`) takes no lock and no reservation, but its outcome
settles the key's cache by the same three rules (`pinned`): once accepted, the cached next
nonce moves past it (past a batch's last nonce) if it was at or beyond the cached value, so
a later managed call does not reuse it; a refusal leaves the cache alone; any other outcome
drops it.
"""

from typing_extensions import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import asyncio
import itertools

from ..core.envelope import INVALID_NONCE, error_code
from ..core.exc import ApiError, AuthError, BadRequest, RateLimited


@dataclass
class NonceManager:
  """Optimistic, locally incremented nonces for a fixed set of API keys."""

  api_key_indices: tuple[int, ...]
  """Keys to rotate across, in order. An explicitly requested key outside them (the slot a
  `ChangePubKey` registers) is tracked the same way, but never rotated to."""
  fetch: Callable[[int], Awaitable[int]]
  """Fetches the next nonce of one key from the venue."""
  cached: dict[int, int] = field(default_factory=dict, init=False)
  """Cached next nonce per key."""
  locks: dict[int, asyncio.Lock] = field(default_factory=dict, init=False, repr=False)
  """Per-key lock, held from signing through submission."""
  rotation: 'itertools.cycle[int]' = field(init=False, repr=False)
  """Round-robin iterator over `api_key_indices`."""

  def __post_init__(self):
    """Start the rotation at the first key."""
    self.rotation = itertools.cycle(self.api_key_indices)

  def lock(self, api_key_index: int) -> asyncio.Lock:
    """The lock serializing `api_key_index`'s transactions."""
    if (lock := self.locks.get(api_key_index)) is None:
      lock = self.locks[api_key_index] = asyncio.Lock()
    return lock

  @asynccontextmanager
  async def reserve(
    self, api_key_index: int | None = None, *, count: int = 1
  ) -> AsyncIterator[tuple[int, int]]:
    """Hold one key's next `count` nonces, as `(api_key_index, first nonce)`, for one
    submission: a single transaction, or a batch signed with consecutive nonces.

    The outcome of the block settles all `count` nonces together: a clean exit consumes
    them, and an exception applies the rules in the module docstring.

    Args:
      api_key_index: Key to use; defaults to the next one in rotation.
      count: How many consecutive nonces to hold.

    Raises:
      BadRequest: `count` is below 1.
    """
    if count < 1:
      raise BadRequest(f'count must be at least 1, got {count}')
    key = next(self.rotation) if api_key_index is None else api_key_index
    async with self.lock(key):
      if key not in self.cached:
        self.cached[key] = await self.fetch(key)
      nonce = self.cached[key]
      try:
        yield key, nonce
      except ApiError as e:
        if not unconsumed(e):
          self.cached.pop(key, None)
        raise
      except BaseException:
        self.cached.pop(key, None)
        raise
      else:
        self.advance(api_key_index=key, next_nonce=nonce + count)

  def advance(self, *, api_key_index: int, next_nonce: int):
    """Move a key's cached next nonce forward to `next_nonce`, never back.

    A key with no cached value is left to be fetched on its next use.

    Args:
      api_key_index: The key.
      next_nonce: The nonce its next transaction should take.
    """
    if (current := self.cached.get(api_key_index)) is not None:
      self.cached[api_key_index] = max(current, next_nonce)

  @asynccontextmanager
  async def pinned(self, *, api_key_index: int, nonce: int) -> AsyncIterator[None]:
    """Track one submission signed with caller-chosen nonces.

    Takes no lock (the caller owns ordering, and may already hold this key's reservation).
    The outcome settles the cache by the same rules as `reserve`: a clean exit, meaning the
    submission was accepted, advances the cached next nonce to `nonce + 1` when `nonce` is
    at or past it; a refusal (`unconsumed`) leaves the cache untouched; anything else is an
    unknown outcome (the transaction may have landed), so the key's cached nonce is dropped
    and refetched on its next use.

    Args:
      api_key_index: Key the submission is signed with.
      nonce: The pinned nonce: the last one, for a batch.
    """
    try:
      yield
    except ApiError as e:
      if not unconsumed(e):
        self.cached.pop(api_key_index, None)
      raise
    except BaseException:
      self.cached.pop(api_key_index, None)
      raise
    self.advance(api_key_index=api_key_index, next_nonce=nonce + 1)


def unconsumed(error: ApiError) -> bool:
  """Whether a rejection certainly left its nonce unconsumed: a refusal (`BadRequest`,
  `AuthError`, `RateLimited`) carrying a business code other than `21104`."""
  code = error_code(error)
  return (
    code is not None
    and code != INVALID_NONCE
    and isinstance(error, (BadRequest, AuthError, RateLimited))
  )
