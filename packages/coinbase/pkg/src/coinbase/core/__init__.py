"""Coinbase client core: transport, authentication, and error mapping for both the v2
and v3 REST families and the Advanced Trade WebSocket.
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
