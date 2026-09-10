# Get Asset Transfers

Use `client.transfers(network='<network>')` for the `alchemy_getAssetTransfers`
JSON-RPC method.

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  transfers = await client.transfers(network='ethereum').get_asset_transfers(
    category=['erc20'],
    from_address='0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    max_count='0x5',
    with_metadata=True,
  )
  print(transfers['transfers'])
```

Use pagination when the response includes `pageKey`:

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  pages = client.transfers(network='ethereum').get_asset_transfers_paged(
    category=['erc20'],
    from_address='0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    max_count='0x5',
    with_metadata=True,
  )
  async for transfers in pages:
    print(transfers)
```
