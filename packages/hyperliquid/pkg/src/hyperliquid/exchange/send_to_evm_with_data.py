from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import (
  ExchangeMixin,
  ExchangeResponse,
  sign_user_signed_action,
)


class SendToEvmWithDataAction(TypedDict):
  type: Literal['sendToEvmWithData']
  token: str
  amount: str
  sourceDex: str
  destinationRecipient: str
  addressEncoding: Literal['hex', 'base58']
  destinationChainId: int
  gasLimit: int
  data: str
  signatureChainId: str
  nonce: int


class SendToEvmWithDataResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[SendToEvmWithDataResult])


class SendToEvmWithData(ExchangeMixin):
  async def send_to_evm_with_data(
    self,
    *,
    token: str,
    amount: str,
    source_dex: str,
    destination_recipient: str,
    address_encoding: Literal['hex', 'base58'],
    destination_chain_id: int,
    gas_limit: int,
    data: str,
    signature_chain_id: str,
    nonce: int | None = None,
  ) -> ExchangeResponse[SendToEvmWithDataResult]:
    """Specialized Core-to-EVM transfer with an additional data payload, through Hyperliquid POST /exchange using the user-signed `sendToEvmWithData` action. The linked HyperEVM contract's `coreReceiveWithData` is called instead of a plain transfer; it is the caller's responsibility to ensure the token is linked and the contract implements that interface.

    Args:
      token: Token to send, in `tokenName:tokenId` format (e.g. "PURR:0xc4bf3f870c0e9465323c0b6ed28096c2").
      amount: Token amount to send, as a decimal string (e.g. "0.01").
      source_dex: Name of the perp DEX to transfer from. Use an empty string for the default USDC perp DEX.
      destination_recipient: Recipient address on the destination EVM chain, encoded per `address_encoding`.
      address_encoding: Encoding used for `destination_recipient`.
      destination_chain_id: Destination EVM chain id.
      gas_limit: Gas limit for the destination call.
      data: Hex-encoded calldata passed to the destination contract's `coreReceiveWithData`.
      signature_chain_id: Hex-encoded chain id used when signing the action, e.g. "0xa4b1" for Arbitrum.
      nonce: Optional action nonce. Defaults to the current timestamp.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now() if nonce is None else nonce
    action: SendToEvmWithDataAction = {
      'type': 'sendToEvmWithData',
      'nonce': ts,
      'token': token,
      'amount': amount,
      'sourceDex': source_dex,
      'destinationRecipient': destination_recipient,
      'addressEncoding': address_encoding,
      'destinationChainId': destination_chain_id,
      'gasLimit': gas_limit,
      'data': data,
      'signatureChainId': signature_chain_id,
    }
    signed_action, sig = sign_user_signed_action(
      action,
      wallet=self.wallet,
      payload_types=[
        {'name': 'hyperliquidChain', 'type': 'string'},
        {'name': 'token', 'type': 'string'},
        {'name': 'amount', 'type': 'string'},
        {'name': 'sourceDex', 'type': 'string'},
        {'name': 'destinationRecipient', 'type': 'string'},
        {'name': 'addressEncoding', 'type': 'string'},
        {'name': 'destinationChainId', 'type': 'string'},
        {'name': 'gasLimit', 'type': 'string'},
        {'name': 'data', 'type': 'string'},
        {'name': 'nonce', 'type': 'uint64'},
      ],
      primary_type='HyperliquidTransaction:SendToEvmWithData',
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
