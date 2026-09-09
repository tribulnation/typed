from dataclasses import dataclass as _dataclass
from .eth_balance import EthBalance
from .token_balance import Token
from typing_extensions import TypeAlias as _TypeAlias
from .core import mixin as _mixin

Network: _TypeAlias = _mixin.Network
"""Supported network names for the public node helpers."""
ALCHEMY_NODE_URLS: dict[Network, str] = _mixin.ALCHEMY_NODE_URLS
"""Hosted-provider URL templates, keyed by network."""
PUBLIC_NODE_URLS: dict[Network, str] = _mixin.PUBLIC_NODE_URLS
"""Public node URLs, keyed by network."""

@_dataclass
class NodeRpc(
  EthBalance,
  Token,
):
  ...
