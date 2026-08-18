from datetime import datetime
from typing_extensions import Literal, NotRequired, TypedDict, deprecated
from bit2me.types import Rate
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Transaction(TypedDict):
  """Network transaction"""

  confirmedAt: NotRequired[datetime]
  """When the transaction was confirmed (ISO 8601)."""
  confirmationCount: NotRequired[float]
  """The number of confirmations the transaction has."""


DestinationKeywords = TypedDict(
  'DestinationKeywords', {'class': Literal['pocket', 'network', 'b2m', 'bankAccount']}
)
"""
  - `class`:   Type of the destination:
    - pocket: destination is another pocket
    - network: destination is an cryptocurrency address
    - b2m: destination is another Bit2Me user
    - bankAccount: destination is a bank account

"""


class Destination(DestinationKeywords):
  """Destination of the transaction"""

  currency: NotRequired[str]
  """The destination currency"""
  amount: NotRequired[str]
  """The total amount of "money" that the destination receives"""
  pocketName: str
  """The destination pocket name"""
  pocketId: str
  """The destination pocket ID"""
  address: NotRequired[str]
  """The destination address"""
  addressNetwork: NotRequired[str]
  """The destination address network"""
  addressInBlacklist: NotRequired[bool]
  """Indicates if destination address is in blacklist"""
  rate: NotRequired[Rate]


OriginKeywords = TypedDict(
  'OriginKeywords',
  {'class': Literal['pocket', 'network', 'b2m', 'card', 'bank transfer']},
)
"""
  - `class`:   Type of the origin:
    - pocket: origin is another pocket
    - network: origin is a cryptocurrency address
    - b2m: origin is another Bit2Me user
    - card: origin is a credit or debit card
    - bank transfer: origin is a bank transfer

"""


class Origin(OriginKeywords):
  """Origin of the transaction"""

  currency: NotRequired[str]
  """The currency of the origin (only present for "outcome transactions")"""
  amount: NotRequired[str]
  """The total amount of "money" that is taken from origin (only present for "outcome transactions")"""
  pocketId: str
  """The destination pocket ID of the transaction (null when class is "pocket" or "b2m")"""
  pocketName: str
  """The destination pocket name (null when class is "pocket" or "b2m")"""
  rate: NotRequired[Rate]


class DataItem(TypedDict):
  id: str
  """The transaction identifier"""
  date: str
  """When the transaction was created (ISO 8601)"""
  type: Literal['deposit', 'withdrawal', 'transfer']
  """Type of the transaction"""
  concept: str
  """The concept of the transaction"""
  origin: Origin
  destination: Destination
  transaction: NotRequired[Transaction]


class ListWalletTransactionsResponse(TypedDict):
  total: float
  """Number of returned entries"""
  data: list[DataItem]
  """Transactions returned"""


validate_response = validator(ListWalletTransactionsResponse)


class List(RpcEndpoint):
  @deprecated('Deprecated method')
  async def list(
    self,
    *,
    pocket_id: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    keyword: str | None = None,
    type: Literal['transfer', 'withdrawal', 'deposit'] | None = None,
    subtype: Literal[
      'purchase',
      'sell',
      'manual-send',
      'automatic-send',
      'manual-transfer',
      'funding',
      'receive',
      'transfer',
      'swap',
      'reimbursement',
      'earn',
      'launchpad-purchase',
    ]
    | None = None,
    method: Literal[
      'pocket',
      'blockchain',
      'card',
      'bank',
      'bank-transfer',
      'profit-share',
      'promo-referral',
    ]
    | None = None,
    from_: datetime | None = None,
    to: datetime | None = None,
    user_currency: str | None = None,
    validate: bool | None = None,
  ) -> ListWalletTransactionsResponse:
    """Return all transactions related to a pocket. If `pocketId` is not specified, all user transactions are returned.

    Transactions can be paginated with `offset` and `limit`. For example, to fetch the third page with 20 records per page:

    ```text
    /v1/wallet/transaction?offset=40&limit=20
    ```

    Multiple filters can be applied when retrieving transactions. For example:

    ```text
    /v1/wallet/transaction?pocketId=9a2dfa96-2fb8-4b76-a9bd-83949c417540&type=deposit
    ```

    Args:
      pocket_id: The pocket identifier to get the transactions or comma delimited list of pocket IDs
      offset: Specify the number of entries to be skipped (0 by default)
      limit: Specify the maximum number of entries to be returned (20 by default)
      keyword: Specify a list (comma-separated values) of keywords to be used to filter the query
      type: Specify the transaction type to filter the entries to be returned (or comma delimited list of types)
      subtype: Specify the transaction subtype to filter the entries to be returned (or comma delimited list of subtypes)
      method: Specify the transaction method to filter the entries to be returned (or comma delimited list of methods)
      from_: Specify the start date (ISO 8601) to filter the date (mandatory if the to parameter is set)
      to: Specify the end date (ISO 8601) to filter the date (mandatory if the from parameter is set)
      user_currency: The user's currency (used to show a rate from it to Euro)
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/wallet/GET/v1/wallet/transaction)
    """
    params = {}
    if pocket_id is not None:
      params['pocketId'] = pocket_id
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    if keyword is not None:
      params['keyword'] = keyword
    if type is not None:
      params['type'] = type
    if subtype is not None:
      params['subtype'] = subtype
    if method is not None:
      params['method'] = method
    if from_ is not None:
      params['from'] = from_
    if to is not None:
      params['to'] = to
    if user_currency is not None:
      params['userCurrency'] = user_currency
    return await self.authed_request(
      'GET',
      '/v1/wallet/transaction',
      params=params,
      validator=validate_response,
      validate=validate,
    )
