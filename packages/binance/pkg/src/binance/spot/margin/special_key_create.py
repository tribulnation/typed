from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CreateSpecialKeyResponse(TypedDict):
  """The created special key."""

  apiKey: NotRequired[str]
  """Generated API key."""
  secretKey: NotRequired[str]
  """Generated HMAC secret key. Null when creating an RSA or Ed25519 key, since those pair with the caller-supplied `publicKey` instead of a Binance-generated secret."""
  type: NotRequired[str]
  """Encryption type of the created key, e.g. HMAC_SHA256 or RSA."""


class SpecialKeyCreate(RpcEndpoint):
  """Create a special (low-latency trading) API key, available to VIP7+ users. Defaults to an HMAC-SHA256 key; pass `publicKey` to create an RSA or Ed25519 key instead. Omit `symbol` to create a cross margin special key, or set it to create an isolated margin symbol's special key."""

  async def special_key_create(
    self,
    *,
    api_name: str,
    symbol: str | None = None,
    ip: str | None = None,
    public_key: str | None = None,
    permission_mode: Literal['TRADE', 'READ'] | None = None,
    validate: bool | None = None,
  ) -> CreateSpecialKeyResponse:
    """Create a special (low-latency trading) API key, available to VIP7+ users. Defaults to an HMAC-SHA256 key; pass `publicKey` to create an RSA or Ed25519 key instead. Omit `symbol` to create a cross margin special key, or set it to create an isolated margin symbol's special key.

    Args:
      api_name: Name for the new special key.
      symbol: Isolated margin trading pair, e.g. BTCUSDT. Omit to create a cross margin special key; set to create an isolated margin symbol's special key instead.
      ip: Trusted IP addresses to whitelist, comma-separated. Can be added in batches; max 30 per API key.
      public_key: URL-encoded RSA or Ed25519 public key. When supplied, the created key uses that asymmetric algorithm instead of the default HMAC-SHA256.
      permission_mode: Permission mode, applicable only to Ed25519 keys (no effect for HMAC-SHA256 or RSA keys). `TRADE` grants all permissions; `READ` grants USER_DATA and FIX_API_READ_ONLY. Defaults to `TRADE`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#create-special-key)
    """
    params: dict = {
      'apiName': api_name,
    }
    if symbol is not None:
      params['symbol'] = symbol
    if ip is not None:
      params['ip'] = ip
    if public_key is not None:
      params['publicKey'] = public_key
    if permission_mode is not None:
      params['permissionMode'] = permission_mode
    _Response = CreateSpecialKeyResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/margin/apiKey',
      params=params,
      validator=_validator,
      validate=validate,
    )
