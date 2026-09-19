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

## Internal transfers by network

`internal` means native-token transfers performed by smart contracts during execution.
It is not available on every network that accepts other transfer categories.

| Network selector | `internal` category |
| --- | --- |
| `ethereum`, `polygon`, `base` | Supported on mainnet |
| `arbitrum`, `optimism`, `bnb`, `avalanche`, `gnosis`, `celo`, `hyperevm` | Not supported |

This table describes the `internal` category only; it does not promise that the Transfers
API or every other category is available on every listed network. The method accepts the
same category values on all networks, so check support before sending the request.

Alchemy also lists Arc Mainnet and Testnet for internal transfers; these do not have
named selectors in this client. See the
[upstream method reference](https://www.alchemy.com/docs/data/transfers-api/transfers-endpoints/alchemy-get-asset-transfers)
and [current feature support](https://www.alchemy.com/docs/reference/feature-support-by-chain).
