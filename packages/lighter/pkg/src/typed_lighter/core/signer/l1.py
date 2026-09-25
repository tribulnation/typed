"""Ethereum L1 signatures, for the transactions that carry one besides the L2 signature.

`ChangePubKey` always needs one; a `Transfer` to another master account and an
`ApproveIntegrator` with non-zero fees do too. The transaction's `l1_message` is signed with
EIP-191 `personal_sign` by the account's L1 wallet, and the `0x` hex signature goes into
`tx_info` as `L1Sig`. It never enters the L2 hash.

`eth-account` is imported inside `eth_sign` rather than at module top: this module is loaded
with every client (`account.AccountSigner` imports it), and `eth-account` takes longer to
import than the rest of the package, while most clients never make an L1 signature.
"""

from dataclasses import replace
import json

from ..exc import BadRequest
from .txs.base import SignedTx, go_json


def eth_sign(message: str, *, eth_private_key: str) -> str:
  """EIP-191 `personal_sign` of `message`: 65 bytes (r, s, v = 27/28) as `0x` hex.

  Args:
    message: The L1 message to sign.
    eth_private_key: Hex private key of the account's L1 (Ethereum) wallet.
  """
  from eth_account import Account
  from eth_account.messages import encode_defunct

  signature = Account.sign_message(
    encode_defunct(text=message), private_key=eth_private_key
  )
  return '0x' + bytes(signature.signature).hex()


def l1_sign(signed: SignedTx, eth_private_key: str) -> SignedTx:
  """Add the L1 wallet's `L1Sig` to an already signed transaction that carries a `message_to_sign`.

  Args:
    signed: A signed `ChangePubKey`, `Transfer` or `ApproveIntegrator`.
    eth_private_key: Hex private key of the account's L1 (Ethereum) wallet.

  Raises:
    BadRequest: The transaction carries no `message_to_sign`.
  """
  if signed.message_to_sign is None:
    raise BadRequest(f'tx type {signed.tx_type} carries no L1 signature')
  body = json.loads(signed.tx_info)
  body['L1Sig'] = eth_sign(signed.message_to_sign, eth_private_key=eth_private_key)
  return replace(signed, tx_info=go_json(body))
