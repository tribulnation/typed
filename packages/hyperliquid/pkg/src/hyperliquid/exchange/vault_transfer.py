from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class VaultTransferAction(TypedDict):
  type: Literal['vaultTransfer']
  vaultAddress: str
  isDeposit: bool
  usd: float
  expiresAfter: NotRequired[int]


class VaultTransferResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[VaultTransferResult])


class VaultTransfer(ExchangeMixin):
  async def vault_transfer(
    self,
    *,
    vault_address: str,
    is_deposit: bool,
    usd: float,
    expires_after: int | None = None,
  ) -> ExchangeResponse[VaultTransferResult]:
    """Add or remove funds from a vault through Hyperliquid POST /exchange using the L1 `vaultTransfer` action.

    Args:
      vault_address: Vault address, 42-character hexadecimal.
      is_deposit: Whether to deposit into the vault (`true`) instead of withdrawing from it (`false`).
      usd: USD amount to deposit or withdraw.
      expires_after: Optional expiration timestamp, in epoch milliseconds, for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: VaultTransferAction = {
      'type': 'vaultTransfer',
      'vaultAddress': vault_address,
      'isDeposit': is_deposit,
      'usd': usd,
    }
    if expires_after is not None:
      action['expiresAfter'] = expires_after
    sig = sign_l1_action(
      action,
      wallet=self.wallet,
      nonce=ts,
      mainnet=self.mainnet,
      vault_address=None,
      expires_after=expires_after,
    )
    result = await self.client.request(
      {
        'action': action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': None,
        'expiresAfter': expires_after,
      }
    )
    return adapter.validate_python(result) if self.validate else result
