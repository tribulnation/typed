# Sign Offline

`client.signer` signs every Lighter transaction type locally, with no network access and no
nonce bookkeeping: you pass the nonce, it returns a `SignedTx`. Use it to pre-sign
transactions, to sign on one machine and submit from another, or to build batches
([Batch Transactions](batch-transactions.md)).

## Sign Without Sending

Building a client opens no connection, so `Lighter.new(...)` with API keys is enough to
sign. Each `client.tx` transaction method has a signer twin of the same name, taking the
same arguments in the same shapes, plus an explicit `nonce`. The exceptions are
`fast_withdraw` and `lit_lease`: they submit to their own REST endpoints rather than
`sendTx`, so `client.signer` has no twin for them: send them through `client.tx` only.

```python
from typed_lighter import Lighter

client = Lighter.new()  # LIGHTER_ACCOUNT_INDEX, LIGHTER_API_KEY_INDEX, LIGHTER_API_PRIVATE_KEY

async with client:
  key = client.signer.api_key_indices[0]
  next_nonce = await client.api.account.keys.next_nonce(
    account_index=client.signer.account_index, api_key_index=key
  )

signed = client.signer.create_order(
  {
    'order_type': 'limit',
    'market_index': 0,
    'client_order_index': 1001,
    'base_amount': 500,
    'is_ask': False,
    'price': 200_000,
    'time_in_force': 'post-only',
  },
  nonce=next_nonce['nonce'],
  api_key_index=key,
)
print(signed.tx_type, signed.tx_hash)  # the hash Lighter will report
print(signed.tx_info)                 # the signed body, as JSON
```

Signing itself needs no connection; only the nonce comes from Lighter. It has to be the
key's next nonce, exactly: `api.account.keys.next_nonce` as above, or
`client.tx.reserve_nonces(...)` when the same client also sends transactions on that key
([Batch Transactions](batch-transactions.md)), so the two never hand out the same one.

The hash is known before anything is sent. Submit the transaction with
`client.tx.send(signed)`, or post `tx_type` and `tx_info` to Lighter's `sendTx` yourself,
before it expires: a signed transaction carries an `expires_at`, 10 minutes after signing
by default, after which Lighter refuses it. Pass `expires_at=` (a timezone-aware
`datetime`) to sign for longer.
`client.tx.create_order(order)` and `client.signer.create_order(order, nonce=...)` take the
same `order`, so code switches between sending now and signing ahead without reshaping
anything; the same holds for grouped orders, cancel-all and integrator approvals.

Every twin also takes `api_key_index` (the first configured key by default), `expires_at`
(when Lighter stops accepting the transaction; 10 minutes from signing by default; a naive
`datetime` raises `BadRequest`), and
`skip_nonce`, which lets Lighter accept any higher nonce instead of exactly the next one.

## Without A Client

The signer stands alone too. Pick the chain id of the network the transaction is for; it
is part of every transaction hash:

```python
import os

from typed_lighter import AccountSigner
from typed_lighter.core import NETWORKS

signer = AccountSigner.new(
  account_index=int(os.environ['LIGHTER_ACCOUNT_INDEX']),
  api_keys={4: os.environ['LIGHTER_API_PRIVATE_KEY']},
  chain_id=NETWORKS['mainnet'].chain_id,
)
nonce = int(os.environ['NEXT_NONCE'])  # key 4's next nonce, fetched where there is a connection
cancel = signer.cancel_all_orders({'mode': 'immediate'}, nonce=nonce)  # expires in 10 minutes
token = signer.auth_token()  # a 10-minute auth token for REST reads and private streams
```

The nonce still has to be the key's next one, read from `GET /api/v1/nextNonce`
(`api.account.keys.next_nonce`) wherever there is a connection, and the transaction has to
reach Lighter before its `expires_at`.

## Keys And Tokens

```python
from datetime import datetime, timedelta, timezone

from typed_lighter import Lighter
from typed_lighter.core.signer import generate_api_key

key = generate_api_key()  # fresh key pair: register it with change_api_key(key.private_key, ...)

client = Lighter.new()
token = client.signer.auth_token(expires_at=datetime.now(timezone.utc) + timedelta(hours=8))
```

A token carries only its expiry: it is valid from the moment it is signed until then, and
Lighter rejects any token whose expiry is more than 8 hours ahead
(`20013 invalid auth: invalid deadline`), so a token cannot be signed now for a later
window. `auth_token` raises `BadRequest` for such an expiry before signing. For access
that outlives 8 hours without an API key, use a read-only token
([Authenticated Setup](../authenticated-setup.md#auth-tokens)).

## Custom Signing Backends

The only secret-holding part is the `Signer` protocol: a `public_key` and a `sign` method
over a 40-byte hash. Pass any implementation in place of a hex key, for example one backed
by a hardware module or a remote signing service, and every transaction type works
unchanged:

```python
from typed_lighter import Lighter, PythonSigner

client = Lighter.new(account_index=476, api_keys={4: PythonSigner.generate()})
```

## Performance And Side Channels

Signing is pure Python: a transaction or token takes a few milliseconds on a typical
machine. It is **not constant-time**: someone able to time many signatures on the same
machine could in principle learn about the key. Signature nonces are hedged (fresh
randomness mixed with the key and message), so a weak random source alone does not leak
the key. Keep signing on hardware you control.

Upstream reference: [API keys](https://apidocs.lighter.xyz/docs/api-keys).
