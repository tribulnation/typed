"""`tx.send`: submit one transaction signed beforehand with `client.signer`."""

from typing_extensions import Literal

from typed_core.validation import validator

from ..core.signer.txs.base import SignedTx
from ..schemas import SendTxResponse
from .core import TxCore, signed_position


class Send(TxCore):
  """Submit a pre-signed transaction (`sendTx`, WebSocket `jsonapi/sendtx`)."""

  async def send(
    self,
    signed: SignedTx,
    *,
    transport: Literal['http', 'ws'] = 'http',
    validate: bool | None = None,
  ) -> SendTxResponse:
    """Submit one already signed transaction (from `client.signer`) as is: its nonce is the
    one chosen when signing.

    When the transaction is signed for this client's own account and is accepted, the
    client's cached next nonce for its key moves past it (never backwards), as for a
    `client.tx` call with an explicit `nonce`, so later `client.tx` calls do not reuse it.
    A refusal leaves that cache alone; any other failure (an HTTP 5xx, a network error, a
    reply that fails validation) may hide a landed transaction, so the cache is dropped and
    refetched before the key's next `client.tx` call.

    Args:
      signed: The signed transaction.
      transport: Submit over HTTP `sendTx` or the WebSocket connection's `jsonapi/sendtx`.
      validate: Override this call's response validation; falls back to the client-level default when omitted.

    Raises:
      BadRequest: `signed` is not a signed Lighter transaction.

    Examples:
      ```python
      async with client.tx.reserve_nonces(1) as reservation:
        signed = client.signer.cancel_order(
          market_index=0,
          order_index=123,
          nonce=reservation.nonces[0],
          api_key_index=reservation.api_key_index,
        )
        reply = await client.tx.send(signed, transport='ws')
      ```

    References:
      - [Official docs](https://apidocs.lighter.xyz/reference/sendtx)
    """
    key, nonce = signed_position(signed)
    async with self.presigned(key, last_nonce=nonce):
      return await self.submit(
        signed,
        transport=transport,
        validator=validator(SendTxResponse),
        validate=validate,
      )
