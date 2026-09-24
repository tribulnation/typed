"""Bind an existing wallet as a sub-account: a call co-signed by the sub-account wallet.

Hand-written rather than generated: the sub-account wallet is not a wire parameter, and
reaches the core as `RpcEndpoint.request(..., child=...)`.
"""

from typing_extensions import TypedDict

from typed_aster.core.auth import Wallet
from typed_aster.core.endpoint.rpc import RpcEndpoint
from typed_aster.schemas import OperationResult


class Request(TypedDict):
  """Sub-account to bind."""

  childAddress: str
  """Sub-account wallet address."""
  name: str
  """Sub-account name."""


class Bind(RpcEndpoint):
  """Bind an existing wallet as a sub-account of the master account. Co-signed: the sub-account wallet signs first (`childSignature`), then the master wallet. Only whitelisted addresses are supported."""

  async def bind(
    self,
    *,
    child_address: str,
    name: str,
    child: Wallet,
    validate: bool | None = None,
  ) -> OperationResult:
    """Bind an existing wallet as a sub-account of the master account. Co-signed: the sub-account wallet signs first (`childSignature`), then the master wallet. Only whitelisted addresses are supported.

    Args:
      child_address: Sub-account wallet address.
      name: Sub-account name.
      child: Sub-account wallet (or its private key) that co-signs the call.
      validate: Override this call's response validation; falls back to the client-level default when omitted.

    References:
      - [Official docs](https://asterdex.github.io/aster-api-website/futures-v3/account&trades/#bind-sub-account-user_data)
    """
    return await self.request(
      Request(childAddress=child_address, name=name),
      method='POST',
      path='sub-accounts/bind',
      meta={
        'sign': 'main',
        'order': ['childAddress', 'name', 'nonce', 'user', 'childSignature'],
      },
      child=child,
      validate=validate,
      request_type=Request,
      response_type=OperationResult,
    )
