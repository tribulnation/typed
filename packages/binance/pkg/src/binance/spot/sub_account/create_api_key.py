from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CreatedSubAccountApiKey(TypedDict):
  """The created API key."""

  apiName: NotRequired[str]
  """API key name."""
  apiKey: NotRequired[str]
  """API key."""
  secretKey: NotRequired[str]
  """Secret key. Returned only once, on creation; store it securely."""
  canTrade: NotRequired[bool]
  """Spot & Margin trading permission."""
  canMarginLoanRepay: NotRequired[bool]
  """Margin borrow/repay permission."""
  canFuturesTrade: NotRequired[bool]
  """Futures trading permission."""
  canUniversalTransfer: NotRequired[bool]
  """Universal transfer permission."""
  canVanillaOptions: NotRequired[bool]
  """Vanilla options (EAPI) trading permission."""
  status: NotRequired[Literal[1, 2, 3]]
  """IP restriction mode in effect for the key (see the request `status`)."""
  ipList: NotRequired[list[str]]
  """Trusted IP addresses, when `status` is `2`."""


class CreateApiKey(RpcEndpoint):
  """Create a new API key for a sub-account, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    api_name: str,
    status: Literal[1, 2, 3],
    can_trade: bool | None = None,
    can_margin_loan_repay: bool | None = None,
    can_futures_trade: bool | None = None,
    can_universal_transfer: bool | None = None,
    can_vanilla_options: bool | None = None,
    ip_address: str | None = None,
    third_party_name: str | None = None,
    public_key: str | None = None,
    validate: bool | None = None,
  ) -> CreatedSubAccountApiKey:
    """Create a new API key for a sub-account, for the master account.

    Args:
      email: Sub-account email.
      api_name: API key name.
      status: IP restriction mode: `1` = unrestricted, `2` = restrict to trusted IPs (requires `ipAddress`), `3` = restrict to a third-party's IPs (requires `thirdPartyName`).
      can_trade: Spot & Margin trading permission. Defaults to `false`.
      can_margin_loan_repay: Margin borrow/repay permission. Defaults to `false`.
      can_futures_trade: Futures trading permission. Defaults to `false`.
      can_universal_transfer: Universal transfer permission. Defaults to `false`.
      can_vanilla_options: Vanilla options (EAPI) trading permission. Defaults to `false`.
      ip_address: Trusted IP addresses, comma-separated (max 500 characters). Required when `status` is `2`.
      third_party_name: Third-party name. Required when `status` is `3`.
      public_key: Ed25519 public key, for an Ed25519-type API key.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#create-sub-account-api-key)
    """
    params: dict = {
      'email': email,
      'apiName': api_name,
      'status': status,
    }
    if can_trade is not None:
      params['canTrade'] = can_trade
    if can_margin_loan_repay is not None:
      params['canMarginLoanRepay'] = can_margin_loan_repay
    if can_futures_trade is not None:
      params['canFuturesTrade'] = can_futures_trade
    if can_universal_transfer is not None:
      params['canUniversalTransfer'] = can_universal_transfer
    if can_vanilla_options is not None:
      params['canVanillaOptions'] = can_vanilla_options
    if ip_address is not None:
      params['ipAddress'] = ip_address
    if third_party_name is not None:
      params['thirdPartyName'] = third_party_name
    if public_key is not None:
      params['publicKey'] = public_key
    _Response = CreatedSubAccountApiKey
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/sub-account/subAccountApi',
      params=params,
      validator=_validator,
      validate=validate,
    )
