# Paginate Through Results

Many endpoints use cursor-based pagination. We offer `<method_name>_paged(...)` helpers for most endpoints that return an async iterable of pages:

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  async for page in client.indexer.data.get_fills_paged(
    address='dydx1...',
    subaccount=0,
    limit=100,
  ):
    for fill in page['fills']:
      ...
  # instead of
  first_page = await client.indexer.data.get_fills(
    address='dydx1...',
    subaccount=0,
    page=1
  )
```
