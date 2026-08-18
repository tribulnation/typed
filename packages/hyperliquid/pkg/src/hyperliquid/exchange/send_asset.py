from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import (
  ExchangeMixin,
  ExchangeResponse,
  sign_user_signed_action,
)


class SendAssetAction(TypedDict):
  type: Literal['sendAsset']
  destination: str
  sourceDex: str
  destinationDex: str
  token: str
  amount: str
  fromSubAccount: str
  signatureChainId: str
  nonce: int


class SendAssetResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[SendAssetResult])


class SendAsset(ExchangeMixin):
  async def send_asset(
    self,
    *,
    destination: str,
    source_dex: str,
    destination_dex: str,
    token: str,
    amount: str,
    from_sub_account: str,
    signature_chain_id: str,
    nonce: int | None = None,
  ) -> ExchangeResponse[SendAssetResult]:
    """Transfer tokens between perp DEXs, spot balance, users, and/or sub-accounts through Hyperliquid POST /exchange using the user-signed `sendAsset` action. Use an empty string to specify the default USDC perp DEX; only the collateral token can be transferred to or from a perp DEX.

    Args:
      destination: Destination user, subaccount, spot account, or DEX address, 42-character hexadecimal.
      source_dex: Name of the perp DEX to transfer from. Use an empty string for the default USDC perp DEX.
      destination_dex: Name of the perp DEX to transfer to. Use an empty string for the default USDC perp DEX.
      token: Token to send, in `tokenName:tokenId` format (e.g. "PURR:0xc4bf3f870c0e9465323c0b6ed28096c2").
      amount: Token amount to send, as a decimal string (e.g. "0.01").
      from_sub_account: Source subaccount address, 42-character hexadecimal, or an empty string when not sending from a subaccount.
      signature_chain_id: Hex-encoded chain id used when signing the action, e.g. "0xa4b1" for Arbitrum.
      nonce: Optional action nonce. Defaults to the current timestamp.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now() if nonce is None else nonce
    action: SendAssetAction = {
      'type': 'sendAsset',
      'nonce': ts,
      'destination': destination,
      'sourceDex': source_dex,
      'destinationDex': destination_dex,
      'token': token,
      'amount': amount,
      'fromSubAccount': from_sub_account,
      'signatureChainId': signature_chain_id,
    }
    signed_action, sig = sign_user_signed_action(
      action,
      wallet=self.wallet,
      payload_types=[
        {'name': 'hyperliquidChain', 'type': 'string'},
        {'name': 'destination', 'type': 'string'},
        {'name': 'sourceDex', 'type': 'string'},
        {'name': 'destinationDex', 'type': 'string'},
        {'name': 'token', 'type': 'string'},
        {'name': 'amount', 'type': 'string'},
        {'name': 'fromSubAccount', 'type': 'string'},
        {'name': 'nonce', 'type': 'uint64'},
      ],
      primary_type='HyperliquidTransaction:SendAsset',
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
