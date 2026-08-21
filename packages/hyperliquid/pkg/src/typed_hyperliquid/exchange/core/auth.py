"""Exchange action signing: msgpack action-hashing plus the two EIP-712 payload shapes
Hyperliquid signs against ("L1 actions" and "user-signed actions", see
`spec/discovery.md`'s Authentication section). Unlike a header/token-signing venue, the
signature this produces is embedded directly in the request body (`ExchangeRequest`'s
`signature` field) -- built by each leaf endpoint method before it ever reaches the
transport, not attached generically by an `authed_request()`.
"""

from typing_extensions import Any, Mapping, Sequence

import msgpack
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount
from eth_utils import keccak, to_hex  # type: ignore (pyright bug apparently)


def address_to_bytes(address: str) -> bytes:
  """Convert a hex EVM address to bytes."""
  return bytes.fromhex(address[2:] if address.startswith('0x') else address)


def action_hash(
  action: Mapping[str, Any],
  vault_address: str | None,
  nonce: int,
  expires_after: int | None,
) -> bytes:
  """Build the Hyperliquid L1 action hash used for signing."""
  data: bytes = msgpack.packb(action)  # type: ignore
  data += nonce.to_bytes(8, 'big')
  if vault_address is None:
    data += b'\x00'
  else:
    data += b'\x01'
    data += address_to_bytes(vault_address)
  if expires_after is not None:
    data += b'\x00'
    data += expires_after.to_bytes(8, 'big')
  return keccak(data)


def construct_phantom_agent(hash_bytes: bytes, mainnet: bool) -> dict[str, Any]:
  """Build the phantom agent payload for L1 action signing."""
  return {'source': 'a' if mainnet else 'b', 'connectionId': hash_bytes}


def l1_payload(phantom_agent: Mapping[str, Any]) -> dict[str, Any]:
  """Build the EIP-712 payload for Hyperliquid L1 action signing."""
  return {
    'domain': {
      'chainId': 1337,
      'name': 'Exchange',
      'verifyingContract': '0x0000000000000000000000000000000000000000',
      'version': '1',
    },
    'types': {
      'Agent': [
        {'name': 'source', 'type': 'string'},
        {'name': 'connectionId', 'type': 'bytes32'},
      ],
      'EIP712Domain': [
        {'name': 'name', 'type': 'string'},
        {'name': 'version', 'type': 'string'},
        {'name': 'chainId', 'type': 'uint256'},
        {'name': 'verifyingContract', 'type': 'address'},
      ],
    },
    'primaryType': 'Agent',
    'message': phantom_agent,
  }


def sign_inner(wallet: LocalAccount, data: Mapping[str, Any]) -> dict[str, Any]:
  """Sign EIP-712 data and return Hyperliquid's signature shape."""
  structured_data = encode_typed_data(full_message=dict(data))
  signed = wallet.sign_message(structured_data)
  return {'r': to_hex(signed['r']), 's': to_hex(signed['s']), 'v': signed['v']}


def sign_l1_action(
  action: Mapping[str, Any],
  *,
  wallet: LocalAccount,
  vault_address: str | None = None,
  nonce: int,
  expires_after: int | None = None,
  mainnet: bool = True,
) -> dict[str, Any]:
  """Sign an L1 exchange action."""
  hash_bytes = action_hash(action, vault_address, nonce, expires_after)
  phantom_agent = construct_phantom_agent(hash_bytes, mainnet)
  data = l1_payload(phantom_agent)
  return sign_inner(wallet, data)


def user_signed_payload(
  primary_type: str,
  payload_types: Sequence[Mapping[str, str]],
  action: Mapping[str, Any],
) -> dict[str, Any]:
  """Build an EIP-712 payload for user-signed exchange actions."""
  chain_id = int(str(action['signatureChainId']), 16)
  return {
    'domain': {
      'name': 'HyperliquidSignTransaction',
      'version': '1',
      'chainId': chain_id,
      'verifyingContract': '0x0000000000000000000000000000000000000000',
    },
    'types': {
      primary_type: list(payload_types),
      'EIP712Domain': [
        {'name': 'name', 'type': 'string'},
        {'name': 'version', 'type': 'string'},
        {'name': 'chainId', 'type': 'uint256'},
        {'name': 'verifyingContract', 'type': 'address'},
      ],
    },
    'primaryType': primary_type,
    'message': dict(action),
  }


def sign_user_signed_action(
  action: Mapping[str, Any],
  *,
  wallet: LocalAccount,
  payload_types: Sequence[Mapping[str, str]],
  primary_type: str,
  mainnet: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
  """Sign a Hyperliquid user-signed action.

  Returns the finalized action -- with `hyperliquidChain` merged in -- alongside the
  signature. Every caller must send this returned action, not its own input `action`,
  as the request body: `hyperliquidChain` is required on the wire, not just inside the
  EIP-712 payload being signed here.
  """
  action = dict(action)
  action['hyperliquidChain'] = 'Mainnet' if mainnet else 'Testnet'
  data = user_signed_payload(primary_type, payload_types, action)
  return action, sign_inner(wallet, data)
