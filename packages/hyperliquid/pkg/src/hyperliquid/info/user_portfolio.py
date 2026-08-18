from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class PortfolioMetrics(TypedDict):
  """Account-value history, PnL history, and volume for one portfolio period."""

  accountValueHistory: list[tuple[int, str]]
  """Account value sampled over this period."""
  pnlHistory: list[tuple[int, str]]
  """Realized + unrealized PnL sampled over this period."""
  vlm: str
  """Trading volume over this period, as a decimal string."""


class UserPortfolioAction(TypedDict):
  type: Literal['portfolio']
  user: str


adapter = pydantic.TypeAdapter(
  list[
    tuple[
      Literal[
        'day',
        'week',
        'month',
        'allTime',
        'perpDay',
        'perpWeek',
        'perpMonth',
        'perpAllTime',
      ],
      PortfolioMetrics,
    ]
  ]
)


class UserPortfolio(InfoMixin):
  async def user_portfolio(
    self,
    *,
    user: str,
  ) -> list[
    tuple[
      Literal[
        'day',
        'week',
        'month',
        'allTime',
        'perpDay',
        'perpWeek',
        'perpMonth',
        'perpAllTime',
      ],
      PortfolioMetrics,
    ]
  ]:
    """Retrieve a user's account-value history, PnL history, and trading volume, broken out by time period.

    Args:
      user: Address to look up, as a 42-character hexadecimal string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: UserPortfolioAction = {
      'type': 'portfolio',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
