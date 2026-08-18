from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class YieldArenaActivity(TypedDict):
  """One Yield Arena activity."""

  activityId: NotRequired[int]
  """Activity identifier."""
  activityType: NotRequired[Literal['AIRDROP', 'LEADERBOARD', 'EVENT']]
  """Activity category."""
  title: NotRequired[str]
  """Activity title, localized via the `lang` header."""
  description: NotRequired[str]
  """Activity description, localized via the `lang` header."""
  rewardPoolInUsd: NotRequired[str]
  """USD value of the reward pool, as a decimal string."""
  rewardToken: NotRequired[list[str]]
  """Reward token symbols; may be empty."""
  redirectUrl: NotRequired[str]
  """Web URL of the activity landing page."""
  startTime: NotRequired[int | None]
  """Millisecond epoch activity start time; null for activities that are immediately effective."""
  endTime: NotRequired[int | None]
  """Millisecond epoch activity end time; null for activities with no fixed end."""


class YieldArenaActivityPage(TypedDict):
  """This user's available Yield Arena activities."""

  activities: NotRequired[list[YieldArenaActivity]]
  """Available activities."""


class Activities(RpcEndpoint):
  """Get the list of Yield Arena giveaway activities currently available to this user."""

  async def activities(
    self,
    *,
    lang: str | None = None,
    validate: bool | None = None,
  ) -> YieldArenaActivityPage:
    """Get the list of Yield Arena giveaway activities currently available to this user.

    Args:
      lang: Locale tag for `title` and `description` (e.g. `en`, `zh-CN`, `pt-BR`). Defaults to `en`. If the value is missing, malformed, or has no translation configured, content is returned in `en`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/yield-arena#get-yield-arena-activities)
    """
    _Response = YieldArenaActivityPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/earn/arena/activities', validator=_validator, validate=validate
    )
