# Query Event Logs & Raw RPC

Event-log search and Ethereum JSON-RPC passthrough.

## Event Logs

By address, by topic, or both — each takes an optional block range and pages like the
account endpoints:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  by_address = await client.logs.by_address(
    address='0xbd3531da5cf5857e7cfaa92426877b022e612cf8', from_block=12878196, to_block=12878196,
  )
  by_topic = await client.logs.by_topics(
    topic0='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
  )
  combined = await client.logs.by_address_and_topics(
    address='0xbd3531da5cf5857e7cfaa92426877b022e612cf8',
    topic0='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
  )
```

`topic0`/`topic1`/`topic2`/`topic3` filter by indexed event topics; the `topicN_M_opr`
parameters (`'and'` or `'or'`) combine them.

## Raw JSON-RPC

`client.proxy` mirrors the standard Ethereum JSON-RPC methods, routed through Etherscan
instead of a node you run yourself:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  block_number = await client.proxy.eth_block_number()
  block = await client.proxy.eth_get_block_by_number(tag='0x10d4f', boolean='true')
  result = await client.proxy.eth_call(
    to='0xdAC17F958D2ee523a2206206994597C13D831ec7', data='0x18160ddd', tag='latest',
  )
```

Every `proxy` method returns the JSON-RPC response as `dict[str, Any]` — Etherscan passes
these through largely unvalidated, so there's no fixed response schema to type against
beyond the envelope itself. `proxy.eth_send_raw_transaction` broadcasts a signed
transaction and is the one write action in this module.
