from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import (
  ExchangeMixin,
  ExchangeResponse,
  sign_user_signed_action,
)


class SpotSendResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


class SpotTransferAction(TypedDict):
  type: Literal['spotSend']
  destination: str
  token: str
  amount: str
  signatureChainId: str
  time: NotRequired[int]
  nonce: int


adapter = pydantic.TypeAdapter(ExchangeResponse[SpotSendResult])


class SpotTransfer(ExchangeMixin):
  async def spot_transfer(
    self,
    *,
    destination: str,
    token: str,
    amount: str,
    signature_chain_id: str,
    time: int | None = None,
    nonce: int | None = None,
  ) -> ExchangeResponse[SpotSendResult]:
    """Send spot assets to another address through Hyperliquid POST /exchange using the user-signed `spotSend` action. This transfer does not touch the EVM bridge.

    Args:
      destination: Destination address, 42-character hexadecimal (e.g. "0x0000000000000000000000000000000000000000").
      token: Spot token to send, in `tokenName:tokenId` format (e.g. "PURR:0xc4bf3f870c0e9465323c0b6ed28096c2").
      amount: Token amount to send, as a decimal string (e.g. "0.01").
      signature_chain_id: Hex-encoded chain id used when signing the action, e.g. "0xa4b1" for Arbitrum.
      time: Action timestamp in epoch milliseconds, used as the nonce. Defaults to the current timestamp when omitted.
      nonce: Optional action nonce. Defaults to the current timestamp.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now() if nonce is None else nonce
    action: SpotTransferAction = {
      'type': 'spotSend',
      'nonce': ts,
      'destination': destination,
      'token': token,
      'amount': amount,
      'signatureChainId': signature_chain_id,
    }
    if time is not None:
      action['time'] = time
    signed_action, sig = sign_user_signed_action(
      action,
      wallet=self.wallet,
      payload_types=[
        {'name': 'hyperliquidChain', 'type': 'string'},
        {'name': 'destination', 'type': 'string'},
        {'name': 'token', 'type': 'string'},
        {'name': 'amount', 'type': 'string'},
        {'name': 'time', 'type': 'string'},
        {'name': 'nonce', 'type': 'uint64'},
      ],
      primary_type='HyperliquidTransaction:SpotTransfer',
      mainnet=self.mainnet,
    )
    result = await self.client.request(
      {
        'action': signed_action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': None,
        'expiresAfter': None,
      }
    )
    return adapter.validate_python(result) if self.validate else result
