# Error Handling

This client delegates RPC transport and ABI decoding to Web3.py. It does not
export `ApiError`, `AuthError`, `NetworkError` or `ValidationError` from
`typed_ethereum.core`, and does not translate provider failures into typed-core
exceptions.

Invalid addresses, failed RPC calls, unavailable endpoints and incompatible token
contracts propagate the errors raised by Web3.py or its provider. Handle failures
at the application boundary according to the selected provider; do not interpret
a failed balance read as a zero balance.

There is no built-in client-wide retry or completeness guarantee. Avoid logging
secret-bearing RPC URLs or raw provider messages without inspecting their contents.
