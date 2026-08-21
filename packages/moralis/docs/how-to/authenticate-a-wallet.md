# Authenticate A Wallet

`client.auth` implements a Sign-In-With-Ethereum-style flow: request a challenge message,
have the user sign it with their wallet, then verify the signature server-side.

## Request And Verify An EVM Challenge

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  challenge = await client.auth.challenge.request_evm_challenge({
    'domain': 'example.com',
    'uri': 'https://example.com',
    'timeout': 60,
    'chainId': '1',
    'address': '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045',
  })
  # have the end user sign `challenge['message']` with their wallet, then:
  verified = await client.auth.challenge.verify_evm_challenge({
    'message': challenge['message'],
    'signature': '0x...',
  })
  print(verified['profileId'])
```

`request_evm_challenge` returns the message to sign; `verify_evm_challenge` checks the
signature and returns the resulting session, including a stable `profileId` for that
wallet. Equivalent `request_solana_challenge`/`verify_solana_challenge` and
`request_aptos_challenge`/`verify_aptos_challenge` pairs cover the other chain families.

## Bound Addresses

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  addresses = await client.auth.profile.addresses_that_are_bound_to_the_specific_profileid(
    'profile_id...',
  )
  print(addresses)
```

`client.auth.bind` requests and verifies binding (or removing) an additional address to
an existing profile, the same request/verify shape as the challenge flow above.
