"""`private/create_api_key` — `private/create_api_key`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class ApiKey(TypedDict):
  id: int
  """Key identifier."""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch) the key was created."""
  client_id: str
  """Client identifier used for authentication."""
  client_secret: str
  """Client secret, or the MD5 fingerprint of the public key, used for authentication. Shown only in this response."""
  public_key: NotRequired[str]
  """PEM-encoded public key (Ed25519/RSA) used for asymmetric signatures, when configured."""
  max_scope: str
  """Space-separated maximal access scope for tokens generated with this key."""
  enabled: NotRequired[bool]
  """Whether the key is enabled and can be used for authentication."""
  default: bool
  """Whether this is the account default API key (deprecated field, kept for compatibility)."""
  name: NotRequired[str]
  """API key name that can be displayed in the transaction log."""
  enabled_features: NotRequired[list[str]]
  """Enabled advanced on-key features, e.g. `restricted_block_trades`, `block_trade_approval`."""
  ip_whitelist: NotRequired[list[str]]
  """IP addresses whitelisted for this key."""


validate_create_api_key = validator[ApiKey](ApiKey)


class CreateApiKey(RpcEndpoint):
  """`private/create_api_key`."""

  async def create_api_key(
    self,
    *,
    max_scope: str,
    name: str | None = None,
    public_key: str | None = None,
    enabled_features: list[Literal['restricted_block_trades', 'block_trade_approval']]
    | None = None,
    validate: bool | None = None,
  ) -> ApiKey:
    """Creates a new API key with the specified scope and permissions. The response includes both the API key id and the secret; the secret is shown once and is not retrievable afterwards (`private/list_api_keys` never returns it -- though see that endpoint's own notes on an observed exception to this). The new key cannot be granted a broader scope than the authenticating key's own scope. Requires two-factor authentication on the calling session.

    Args:
      max_scope: Maximal access scope for tokens generated with this key, as a space-separated string of `resource:permission` pairs (e.g. `"account:read trade:read block_trade:read_write wallet:none"`) -- observed on the wire as a single string, not the array of strings the venue's own schema types it as (same discrepancy `account.list_api_keys` records for the response field of the same name).
      name: Display name for the key. Letters, numbers and underscores only; maximum length 16 characters.
      public_key: Ed25519 or RSA PEM-encoded public key, for an asymmetric key that signs requests with the holder's own private key instead of a shared secret.
      enabled_features: Advanced on-key features to enable: `restricted_block_trades` scopes block-trade reads to trades made with this key; `block_trade_approval` requires additional user approval for block trades created with this key.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-create_api_key)
    """
    params: dict = {
      'max_scope': max_scope,
    }
    if name is not None:
      params['name'] = name
    if public_key is not None:
      params['public_key'] = public_key
    if enabled_features is not None:
      params['enabled_features'] = enabled_features
    return await self.authed_request(
      'private/create_api_key',
      params=params,
      validator=validate_create_api_key,
      validate=validate,
    )
