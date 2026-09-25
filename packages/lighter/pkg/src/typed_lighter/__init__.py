"""A fully typed, validated async client for the Lighter API.

Examples:
  ```python
  from typed_lighter import Lighter

  async with Lighter.new(public=True) as client:
    books = await client.api.markets.order_books()
    print(books['order_books'][0]['symbol'])
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
