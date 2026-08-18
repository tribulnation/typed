from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class OutcomeTemplatesAction(TypedDict):
  type: Literal['outcomeTemplates']


class QuestionOutcomeTemplateRoleData(TypedDict):
  """Role data for a named outcome template belonging to a question."""

  parent: str
  """Id of the parent question template this named outcome belongs to."""


class StandaloneOutcomeTemplateRoleData(TypedDict):
  """Role data for a standalone (question-less) outcome template."""

  sideNames: list[str]
  """Names of the outcome's two tradeable sides, e.g. `["Yes", "No"]`."""


class QuestionOutcomeTemplateRole(TypedDict):
  """A named outcome template, registered and associated with a parent question."""

  questionOutcome: QuestionOutcomeTemplateRoleData


class StandaloneOutcomeTemplateRole(TypedDict):
  """A standalone outcome template, registered directly without a parent question."""

  standaloneOutcome: StandaloneOutcomeTemplateRoleData


class OutcomeTemplate(TypedDict):
  """One registered HIP-4 outcome/question template."""

  id: str
  """Template id, referenced when registering an outcome/question from this template."""
  role: (
    Literal['question'] | StandaloneOutcomeTemplateRole | QuestionOutcomeTemplateRole
  )
  """What this template registers: a question, a standalone outcome, or a named outcome under a question."""
  name: str
  """Display name pattern, with `{keyword}` placeholders filled in from the template's `keywords` at registration time."""
  description: str
  """Description pattern, with `{keyword}` placeholders filled in from the template's `keywords` at registration time."""
  keywords: list[
    tuple[
      str,
      Literal[
        'dateTime', 'date', 'string', 'shortString', 'hlPerp', 'uInt', 'uDecimal'
      ],
    ]
  ]
  """The template's keyword placeholders and their expected value formats. Empty for a template with no placeholders (e.g. a `questionOutcome` role whose text is fixed)."""


adapter = pydantic.TypeAdapter(list[OutcomeTemplate])


class OutcomeTemplates(InfoMixin):
  async def outcome_templates(self) -> list[OutcomeTemplate]:
    """Retrieve every registered HIP-4 outcome/question template -- the parameterized definitions `registerStandaloneOutcomeFromTemplate`/`registerQuestionFromTemplate`/`registerAndAssociateNamedOutcomeFromTemplate` instantiate by filling in each template's keywords.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions)
    """
    params: OutcomeTemplatesAction = {
      'type': 'outcomeTemplates',
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
