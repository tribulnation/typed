# Manage Webhook Streams

`client.streams` manages Moralis Streams: server-side subscriptions that POST matching
on-chain activity to a webhook URL you host. There is no client-side socket to consume --
`client.streams` only creates and configures the subscription; delivery happens to your
own server.

## Create, List, And Update A Stream

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  stream = await client.streams.evm.create_stream(
    webhook_url='https://example.com/webhook',
    description='USDC transfers',
    chain_ids=['0x1'],
  )
  streams = await client.streams.evm.all_streams(100)
  await client.streams.evm.add_address_to_stream(
    stream['id'], address='0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045',
  )
  await client.streams.evm.update_stream_status(stream['id'], status='active')
  print(stream['id'], streams['result'])
```

`streams.bitcoin` and `streams.solana` create the equivalent per-chain-family streams. A
stream starts `'paused'`; set it `'active'` once its addresses are configured. Status is
one of `'active'`, `'paused'`, `'error'`, or `'terminated'`.

## History And Stats

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  history = await client.streams.history.entries(limit=100)
  stats = await client.streams.stats.account()
  print(history['result'], stats)
```

`streams.history` covers delivered/failed webhook deliveries; `streams.stats` covers
usage against your plan.

## Project Settings

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  settings = await client.streams.settings.project_settings()
  await client.streams.settings.set_project_settings('us-east-1')
  print(settings)
```

`streams.settings` covers the project-wide settings behind every stream on this API key:
the `region` webhooks are posted from, and the `secretKey` used to validate them.
