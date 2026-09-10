# Subscription Boundaries

`NodeRpc` has no `.streams` namespace. Its convenience constructors create HTTP
providers, not WebSocket subscriptions.

A caller may construct an `AsyncWeb3[AsyncBaseProvider]` with a persistent provider
and pass it as `NodeRpc(w3=...)`. The context manager delegates persistent-provider
entry and exit to Web3.py. Subscription, reconnect and buffering behavior belong
to that provider and your application, not an additional guarantee of this wrapper.
