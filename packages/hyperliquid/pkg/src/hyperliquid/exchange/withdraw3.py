from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import (
  ExchangeMixin,
  ExchangeResponse,
  sign_user_signed_action,
)


class Withdraw3action(TypedDict):
  type: Literal['withdraw3']
  amount: str
  destination: str
  signatureChainId: str
  time: NotRequired[int]
  nonce: int


class Withdraw3result(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[Withdraw3result])


class Withdraw3(ExchangeMixin):
  async def withdraw3(
    self,
    *,
    amount: str,
    destination: str,
    signature_chain_id: str,
    time: int | None = None,
    nonce: int | None = None,
  ) -> ExchangeResponse[Withdraw3result]:
    """Initiate the withdrawal flow through Hyperliquid POST /exchange using the user-signed `withdraw3` action. The L1 validators sign and send the request to the bridge contract; withdrawals take roughly 5 minutes to finalize and carry a venue fee.

    Args:
      amount: USDC amount to withdraw, as a decimal string (e.g. "1" for 1 USDC).
      destination: Destination address, 42-character hexadecimal (e.g. "0x0000000000000000000000000000000000000000").
      signature_chain_id: Hex-encoded chain id used when signing the action, e.g. "0xa4b1" for Arbitrum.
      time: Action timestamp in epoch milliseconds, used as the nonce. Defaults to the current timestamp when omitted.
      nonce: Optional action nonce. Defaults to the current timestamp.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now() if nonce is None else nonce
    action: Withdraw3action = {
      'type': 'withdraw3',
      'nonce': ts,
      'amount': amount,
      'destination': destination,
      'signatureChainId': signature_chain_id,
    }
    if time is not None:
      action['time'] = time
    signed_action, sig = sign_user_signed_action(
      action,
      wallet=self.wallet,
      payload_types=[
        {'name': 'hyperliquidChain', 'type': 'string'},
        {'name': 'amount', 'type': 'string'},
        {'name': 'destination', 'type': 'string'},
        {'name': 'time', 'type': 'string'},
        {'name': 'nonce', 'type': 'uint64'},
      ],
      primary_type='HyperliquidTransaction:Withdraw3',
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
