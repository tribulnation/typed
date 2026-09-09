"""Coinbase client core: transport, authentication, and error mapping for both the v2
and v3 REST families and the Advanced Trade WebSocket. Its generic, auth-agnostic pieces
(`RpcClient`/`RpcEndpoint`, `StreamClient`/`StreamEndpoint`, the `typed_core.exceptions`
re-exports, and the `TimestampIso`/`TimestampSeconds` wire-format converters) are also
reused directly by `typed_coinbase.exchange`, a structurally independent sub-client with
its own transport/auth -- see `spec/core.md`'s "Coinbase Exchange Core" section.
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
