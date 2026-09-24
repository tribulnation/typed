"""Create a sub-account for a wallet: a call co-signed by the sub-account wallet.

Hand-written rather than generated: the sub-account wallet is not a wire parameter, and
reaches the core as `RpcEndpoint.request(..., child=...)`.
"""

from typing_extensions import TypedDict

from typed_aster.core.auth import Wallet
from typed_aster.core.endpoint.rpc import RpcEndpoint
from typed_aster.schemas import OperationResult


class Request(TypedDict):
  """Sub-account to create."""

  subSourceAddr: str
  """Sub-account wallet address."""
  subAccountName: str
  """Sub-account name."""


class Create(RpcEndpoint):
  """Create a sub-account for a wallet under the master account. Co-signed: the sub-account wallet signs first (`childSignature`), then the master wallet."""

  async def create(
    self,
    *,
    sub_source_addr: str,
    sub_account_name: str,
    child: Wallet,
    validate: bool | None = None,
  ) -> OperationResult:
    """Create a sub-account for a wallet under the master account. Co-signed: the sub-account wallet signs first (`childSignature`), then the master wallet.

    Args:
      sub_source_addr: Sub-account wallet address.
      sub_account_name: Sub-account name.
      child: Sub-account wallet (or its private key) that co-signs the call.
      validate: Override this call's response validation; falls back to the client-level default when omitted.

    References:
      - [Official docs](https://asterdex.github.io/aster-api-website/futures-v3/account&trades/#create-sub-account-trade)
    """
    return await self.request(
      Request(subSourceAddr=sub_source_addr, subAccountName=sub_account_name),
      method='POST',
      path='createSubAccount',
      meta={
        'sign': 'main',
        'order': [
          'subAccountName',
          'subSourceAddr',
          'nonce',
          'user',
          'signer',
          'childSignature',
        ],
      },
      child=child,
      validate=validate,
      request_type=Request,
      response_type=OperationResult,
    )
