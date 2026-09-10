from decimal import Decimal
from web3.types import Wei, Gwei
from web3 import Web3

def same_address(a: str | bytes, b: str | bytes):
  return Web3.to_checksum_address(a) == Web3.to_checksum_address(b)

def wei2eth(wei: Decimal | int | Wei) -> Decimal:
  return wei / Decimal(10**18)

def gwei2eth(gwei: Decimal | int | Gwei) -> Decimal:
  return gwei / Decimal(10**9)