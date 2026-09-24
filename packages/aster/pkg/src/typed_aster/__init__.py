"""A fully typed, validated async client for the Aster API.

Examples:
  ```python
  from typed_aster import Aster

  async with Aster.new(public=True) as client:
    server_time = await client.futures.market.time()
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
