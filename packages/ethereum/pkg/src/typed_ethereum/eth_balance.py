from dataclasses import dataclass
from decimal import Decimal

from typed_ethereum.core.mixin import NodeRpcMixin
from typed_ethereum.core.units import wei2eth

@dataclass
class EthBalance(NodeRpcMixin):
  async def eth_balance(self, address: str) -> Decimal:
    """Get the ETH balance of an address."""
    wei_balance = await self.w3.eth.get_balance(address) # type: ignore
    return wei2eth(wei_balance)
