# Batch Transactions

Lighter executes a batch of transactions back to back, with no other transaction in
between: a quote refresh that cancels and replaces orders goes through in one step. A
batch is up to 50 transactions over HTTP or 15 over WebSocket, all signed by one API key
of one account, with strictly increasing nonces. The examples use market `0`, mainnet's
ETH perp; on testnet it is `4095` ([Networks](../authenticated-setup.md#networks)).

## Reserve Nonces, Sign, Submit

`client.tx` methods take nonces for you, but a batch is signed ahead of time with
`client.signer`, whose methods take the same arguments as their `client.tx` namesakes plus
a `nonce`, so the nonces have to be reserved first. `fast_withdraw` and `lit_lease` have no
signer twin (they submit to their own REST endpoints), so they cannot go in a batch.
`reserve_nonces(n)` holds `n` consecutive nonces of one key; sign each transaction with
them, then submit with `tx.batch` inside the block:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  async with client.tx.reserve_nonces(3) as reservation:
    key = reservation.api_key_index
    first, second, third = reservation.nonces
    batch = [
      client.signer.cancel_order(market_index=0, order_index=1001, nonce=first, api_key_index=key),
      client.signer.create_order(
        {
          'order_type': 'limit', 'market_index': 0, 'client_order_index': 1011,
          'base_amount': 500, 'is_ask': False, 'price': 199_000, 'time_in_force': 'post-only',
        },
        nonce=second, api_key_index=key,
      ),
      client.signer.create_order(
        {
          'order_type': 'limit', 'market_index': 0, 'client_order_index': 1012,
          'base_amount': 500, 'is_ask': True, 'price': 201_000, 'time_in_force': 'post-only',
        },
        nonce=third, api_key_index=key,
      ),
    ]
    receipt = await client.tx.batch(batch, transport='ws')

  print(receipt['tx_hash'])  # one hash per transaction, in order
```

While the block runs, no other `client.tx` call on that key can take a nonce, so nothing
slips in between. How the block ends settles the reserved nonces:

- a clean exit consumes them all, whether or not anything was sent. Leaving the block
  without submitting skips those nonces, so the **next** transaction on that key fails
  once with `21104` invalid nonce, after which the client refetches the nonce and the
  one after succeeds. Only leave the block after submitting;
- a batch Lighter refused with a business code (a `BadRequest`, `AuthError` or
  `RateLimited` for which `error_code(error)` is not `None`), other than `21104` invalid
  nonce, leaves them unused, ready for the next transaction;
- anything else (`21104`, an HTTP 5xx, a network error or timeout, an error with no
  business code, any other exception) makes the client refetch the key's nonce from
  Lighter before its next transaction.

## Checks Before Sending

`tx.batch` checks the batch before it goes out, and raises `BadRequest` when it is empty,
longer than the transport allows, mixes accounts or API keys, or has nonces out of order.

## Send One Pre-Signed Transaction

`tx.send` submits a single transaction you signed yourself:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  async with client.tx.reserve_nonces(1) as reservation:
    signed = client.signer.cancel_all_orders(
      {'mode': 'immediate'}, nonce=reservation.nonces[0], api_key_index=reservation.api_key_index
    )
    await client.tx.send(signed, transport='ws')
```

`tx.batch` and `tx.send` submit whatever nonces you signed with. When the transactions
are signed for the client's own account and Lighter accepts them, the client's cached
next nonce for that key moves past the last one sent (it never moves backwards), exactly
as for a `client.tx` call with an explicit `nonce`, so later `client.tx` calls do not
reuse them. A failure settles the cache by the same rules as a managed nonce (see
[Error Handling](../reference/error-handling.md#transactions-and-nonces)): a refusal
carrying a business code leaves it as it was, and every other outcome (an HTTP 5xx, a
network error, a reply that fails validation) drops it, to be refetched before that key's
next `client.tx` call. Inside `reserve_nonces`, the block's outcome then settles it as
described above. For signing with no connection at all, see
[Sign Offline](sign-offline.md).

Upstream reference: [Trading](https://apidocs.lighter.xyz/docs/trading).
