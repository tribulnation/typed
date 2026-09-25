"""Pure-Python Lighter signer: L2 transactions, auth tokens and API keys.

A stdlib-only port of lighter-go v1.0.10 and poseidon_crypto v0.0.15: the Goldilocks field
and its quintic extension (`field`), the ECgFp5 curve (`curve`), Poseidon2 (`poseidon2`),
Schnorr signatures (`schnorr`), and the 20 user transaction types with Go-exact validation,
hashing and `tx_info` JSON (`txs`). Golden vectors from the Go code pin all of it.

- `key.Signer` is the one backend boundary (lighter-go's own `Signer` interface: sign a
  40-byte hash); `key.PythonSigner` is the default implementation.
- `account.AccountSigner` is `client.signer`: one account's keys, on one network.
- `l1` adds the Ethereum (EIP-191) signature a few transaction types carry, via
  `eth-account`.

**Signing is not constant-time.** Python integers are variable-time, the generator table is
indexed by digits of the secret nonce, and the loops branch on them, so an attacker who can
time many signatures on the same machine could in principle learn about the key. lighter-go
is not constant-time either (its table lookups branch and it uses `big.Int` for scalars).
Nonces are hedged (random bytes mixed with a hash of the key and message), so a weak or
repeated RNG does not by itself leak the key.
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
