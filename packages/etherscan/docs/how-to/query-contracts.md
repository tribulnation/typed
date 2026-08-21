# Query Contracts

Look up a verified contract's ABI, source, and deployment info.

## ABI

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  abi = await client.contracts.abi(address='0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413')
```

Raises `ApiError` if the contract isn't verified on Etherscan.

## Source Code

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  source = await client.contracts.source_code(address='0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413')
```

Returns the full verified source, compiler settings, and metadata (`CompilerVersion`,
`OptimizationUsed`, `LicenseType`, `SwarmSource`, and more) for each contract entry in
`source['result']`.

## Creation Info

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  creation = await client.contracts.creation(
    contractaddresses='0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413',
  )
```

`contractaddresses` takes one or more comma-separated contract addresses and returns each
one's creator address and creation transaction hash.

## Verification

`contracts.verify_source_code`, `verify_proxy`, `verify_vyper`, `verify_stylus`, and
`verify_zksync_source_code` submit a contract for verification;
`verification_status`/`proxy_verification_status` poll a submission by its GUID. These are
real, typed methods, but submitting a verification is a write action outside the scope of
read-only exploration — check them against
[Etherscan's contract-verification docs](https://docs.etherscan.io/api-reference/endpoint/verifysourcecode)
before using them.
