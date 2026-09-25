"""`tx.batch`: submit several transactions signed beforehand, in one request."""

from typing_extensions import Literal, NotRequired, Sequence, TypedDict

from typed_core.validation import validator

from ..core import TimestampMillis
from ..core.signer.txs.base import SignedTx
from .core import (
  MAX_BATCH_HTTP,
  MAX_BATCH_WS,
  TxCore,
  check_batch,
  signed_position,
)


class SendTxBatchResponse(TypedDict):
  """The API server's acceptance of every transaction of the batch."""

  code: int
  """`200` when accepted."""
  message: NotRequired[str]
  """HTTP only: a JSON-encoded string of extra detail, e.g. `{"ratelimit": "Ratelimit is off"}`."""
  tx_hash: list[str]
  """Hash of each accepted transaction, in request order."""
  predicted_execution_time_ms: TimestampMillis
  """When the sequencer is expected to execute the batch."""
  volume_quota_remaining: NotRequired[int]
  """Premium accounts' remaining volume quota; absent otherwise."""
  id: NotRequired[str]
  """WS only: the request's correlation id, echoed."""
  type: NotRequired[Literal['jsonapi/sendtxbatch']]
  """WS only: the RPC frame type, echoed."""


class Batch(TxCore):
  """Submit pre-signed transactions together (`sendTxBatch`, WebSocket `jsonapi/sendtxbatch`)."""

  async def batch(
    self,
    signed_txs: Sequence[SignedTx],
    *,
    transport: Literal['http', 'ws'] = 'http',
    validate: bool | None = None,
  ) -> SendTxBatchResponse:
    """Submit several already signed transactions (from `client.signer`) in one request.

    The venue runs them back to back, with nothing interleaved. They must all come from
    one account and API key, with strictly increasing nonces: sign them inside
    `tx.reserve_nonces(len(...))` to take those nonces from the client's nonce manager
    (see its example), or pick them yourself. The batch is checked client-side before
    anything is sent. When it is signed for this client's own account and is accepted, the
    client's cached next nonce for its key moves past the last one (never backwards), as
    for a `client.tx` call with an explicit `nonce`. A refusal leaves that cache alone; any
    other failure (an HTTP 5xx, a network error, a reply that fails validation) drops it,
    to be refetched before the key's next `client.tx` call.

    Args:
      signed_txs: The signed transactions, in nonce order: at most 50 over HTTP, 15 over WebSocket.
      transport: Submit over HTTP `sendTxBatch` or the WebSocket connection's `jsonapi/sendtxbatch`.
      validate: Override this call's response validation; falls back to the client-level default when omitted.

    Raises:
      BadRequest: The batch is empty, too long for the transport, mixes accounts or API
        keys, or its nonces do not strictly increase.

    References:
      - [Official docs](https://apidocs.lighter.xyz/reference/sendtxbatch)
    """
    key = check_batch(
      signed_txs, limit=MAX_BATCH_WS if transport == 'ws' else MAX_BATCH_HTTP
    )
    _, last_nonce = signed_position(signed_txs[-1])
    async with self.presigned(key, last_nonce=last_nonce):
      return await self.submit_batch(
        signed_txs,
        transport=transport,
        validator=validator(SendTxBatchResponse),
        validate=validate,
      )
