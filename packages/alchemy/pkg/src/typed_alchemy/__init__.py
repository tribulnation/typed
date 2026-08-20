"""A fully typed, validated async client for the Alchemy Data APIs.

Examples:
  ```python
  from typed_alchemy import Alchemy

  async with Alchemy.new() as client:
    result = await client.token('ethereum').get_token_balances('0x...')
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
