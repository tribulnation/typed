"""Shared Moralis public types."""

from typing_extensions import Literal


Chain = Literal[
  'eth',
  '0x1',
  'sepolia',
  '0xaa36a7',
  'polygon',
  '0x89',
  'bsc',
  '0x38',
  'arbitrum',
  '0xa4b1',
  'base',
  '0x2105',
  'optimism',
  '0xa',
  'avalanche',
  '0xa86a',
  'fantom',
  '0xfa',
  'cronos',
  '0x19',
  'gnosis',
  '0x64',
  'linea',
  '0xe708',
  'moonbeam',
  '0x504',
  'moonriver',
  '0x505',
  'ronin',
  '0x7e4',
  'lisk',
  '0x46f',
  'sei',
  '0x531',
]
"""Moralis EVM chain identifier accepted by wallet endpoints."""

Order = Literal['ASC', 'DESC']
"""Pagination sort order."""

Direction = Literal['receive', 'send']
"""Moralis transfer direction for wallet-relative transfer entries."""
