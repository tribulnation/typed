# Get Asset Transfers

Use `client.transfers('<network>')` for the `alchemy_getAssetTransfers`
JSON-RPC method.

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  transfers = await client.transfers('ethereum').get_asset_transfers({
    'category': ['erc20'],
    'fromAddress': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    'maxCount': '0x5',
    'withMetadata': True,
  })
  print(transfers['transfers'])
```

Use pagination when the response includes `pageKey`:

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  pages = client.transfers('ethereum').get_asset_transfers_paged({
    'category': ['erc20'],
    'fromAddress': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    'maxCount': '0x5',
    'withMetadata': True,
  })
  async for transfers in pages:
    print(transfers)
```
