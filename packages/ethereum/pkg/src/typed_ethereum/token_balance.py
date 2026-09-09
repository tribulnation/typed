from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property

from web3 import Web3, AsyncWeb3
from web3.contract import AsyncContract
from web3.providers import AsyncBaseProvider

from typed_ethereum.core.mixin import NodeRpcMixin

ERC20_ABI = [
  {
    'type': 'function',
    'name': 'balanceOf',
    'constant': True,
    'inputs': [{'name': 'owner', 'type': 'address'}],
    'outputs': [{'name': '', 'type': 'uint256'}],
  },
  {
    'type': 'function',
    'name': 'decimals',
    'constant': True,
    'inputs': [],
    'outputs': [{'name': '', 'type': 'uint8'}],
  },
  {
    'type': 'function',
    'name': 'symbol',
    'constant': True,
    'inputs': [],
    'outputs': [{'name': '', 'type': 'string'}],
  },
]

@dataclass(frozen=True)
class ERC20:
  address: str
  w3: AsyncWeb3[AsyncBaseProvider]

  @cached_property
  def contract(self) -> AsyncContract:
    return self.w3.eth.contract(address=self.address, abi=ERC20_ABI) # type: ignore

  async def symbol(self) -> str:
    return await self.contract.functions.symbol().call()

  async def decimals(self) -> int:
    return await self.contract.functions.decimals().call()

  async def raw_balance(self, address: str) -> int:
    return await self.contract.functions.balanceOf(address).call()

  async def balance(self, address: str) -> Decimal:
    raw_balance = await self.raw_balance(address)
    decimals = await self.decimals()
    return Decimal(raw_balance) / Decimal(10)**decimals

  def decode_input(self, input: str):
    return self.contract.decode_function_input(input)


@dataclass
class Token(NodeRpcMixin):
  def token(self, address: str) -> ERC20:
    """A convenient wrapper for the ERC-20 interface."""
    address = Web3.to_checksum_address(address)
    return ERC20(address=address, w3=self.w3)

  async def token_balance(self, address: str, *, token_address: str) -> Decimal:
    """Get the address' balance of a given ERC-20 token."""
    return await ERC20(address=token_address, w3=self.w3).balance(address)
