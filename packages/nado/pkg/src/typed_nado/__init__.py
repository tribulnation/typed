"""A fully typed, validated async client for the Nado API.

Examples:
  ```python
  from typed_nado import Nado

  async with Nado.new(public=True) as client:
    print(await client.gateway.status())
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
