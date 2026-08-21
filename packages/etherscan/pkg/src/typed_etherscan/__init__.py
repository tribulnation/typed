"""A fully typed, validated async client for the Etherscan API.

Examples:
  ```python
  from typed_etherscan import Etherscan

  async with Etherscan.new() as client:
    result = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
    print(result)
  ```
"""
import lazy_loader as lazy
__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
