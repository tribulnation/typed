"""`private/create_subaccount` — `private/create_subaccount`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class SubaccountCurrencyPortfolio(TypedDict):
  currency: str
  """The currency this portfolio entry is for, lower-case (e.g. `"btc"`)."""
  balance: float
  """The subaccount's balance."""
  locked_balance: NotRequired[float]
  """The subaccount's locked balance (observed live; not in the venue's own published schema for this field)."""
  margin_balance: float
  """The subaccount's margin balance."""
  equity: float
  """The subaccount's current equity."""
  maintenance_margin: float
  """The maintenance margin."""
  initial_margin: float
  """The subaccount's initial margin."""
  available_funds: float
  """The subaccount's available funds."""
  available_withdrawal_funds: float
  """The subaccount's available-to-withdraw funds."""
  spot_reserve: NotRequired[float]
  """The subaccount's balance reserved in active spot orders (observed live; not in the venue's own published schema for this field)."""
  additional_reserve: NotRequired[float]
  """The subaccount's balance reserved in other orders (observed live; not in the venue's own published schema for this field)."""


class TradingProductDetail(TypedDict):
  product: str
  """Trading product name, e.g. `"perpetual"`, `"futures"`, `"options"`, `"future_combos"`, `"option_combos"`, `"spots"`. Not declared `enum`: this field is not documented on this operation at all, so only the observed values are known, not a closed set."""
  enabled: bool
  """Whether this trading product is enabled for the subaccount."""
  overwriteable: NotRequired[bool]
  """Whether this setting can be overridden."""
  requires_consent: NotRequired[bool]
  """Whether enabling this product requires user consent."""


class CreateSubaccountResult(TypedDict):
  id: int
  """Subaccount identifier."""
  username: str
  """System-generated account username."""
  system_name: str
  """System-generated user nickname."""
  type: Literal['subaccount']
  """Account type."""
  email: str
  """Email address currently associated with the subaccount."""
  login_enabled: bool
  """Whether direct login to the subaccount is enabled."""
  is_password: bool
  """Whether a password has been configured for the subaccount."""
  receive_notifications: bool
  """When `true`, all notification emails are received on the main account's email instead."""
  security_keys_enabled: bool
  """Whether Security Keys authentication is enabled."""
  security_keys_assignments: list[str]
  """Names of assignments with Security Keys assigned."""
  margin_model: str
  """Name of the subaccount's margin model."""
  disabled_trading_products: list[str]
  """Trading products disabled for this subaccount."""
  trading_products_details: list[TradingProductDetail]
  """Per-product trading enablement details."""
  proof_id: str
  """Hashed identifier used in the Proof of Liability for the subaccount. Sensitive: keep secret to avoid disclosing entries in the Proof-of-Reserves files."""
  proof_id_signature: str
  """Signature used as a base string for the `proof_id` hash. Sensitive, for the same reason as `proof_id`."""
  referrals_count: int
  """Number of referrals."""
  portfolio: NotRequired[dict[str, SubaccountCurrencyPortfolio]]
  """Per-currency portfolio detail for the new subaccount, keyed by lower-case currency code -- all zero on creation."""


validate_create_subaccount = validator[CreateSubaccountResult](CreateSubaccountResult)


class CreateSubaccount(RpcEndpoint):
  """`private/create_subaccount`."""

  async def create_subaccount(
    self,
    *,
    validate: bool | None = None,
  ) -> CreateSubaccountResult:
    """Creates a new subaccount under the main account, with default settings and a system-generated username. Takes no parameters; use the other subaccount-management methods afterwards to configure it (rename, email, login, trading products, ...).

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-create_subaccount)
    """
    return await self.authed_request(
      'private/create_subaccount',
      validator=validate_create_subaccount,
      validate=validate,
    )
