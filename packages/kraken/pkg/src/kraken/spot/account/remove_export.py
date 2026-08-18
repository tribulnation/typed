"""`spot.account.remove_export` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class RemoveExportResult(TypedDict):
  """Outcome of the delete/cancel operation. Exactly one of `delete`/`cancel` is present, matching the requested `type`."""

  delete: NotRequired[bool]
  """Whether deletion succeeded. Present when `type: "delete"` was requested."""
  cancel: NotRequired[bool]
  """Whether cancellation succeeded. Present when `type: "cancel"` was requested."""


validate_remove_export = validator(RemoveExportResult)


class RemoveExport(RpcEndpoint):
  """`spot.account.remove_export`."""

  async def remove_export(
    self,
    *,
    id: str,
    type: Literal['cancel', 'delete'],
  ) -> RemoveExportResult:
    """Delete an exported trades/ledgers report. `delete` can only be used for reports that have already been processed; use `cancel` for reports that are still queued or processing.

    **API Key Permissions Required:** `Data - Export data`

    Args:
      id: ID of the report to delete or cancel.
      type: `delete` can only be used for reports that have already been processed. Use `cancel` for queued or processing reports.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/delete-export-report)
    """
    data: dict = {
      'id': id,
      'type': type,
    }

    return await self.authed_request(
      '/0/private/RemoveExport', data, validator=validate_remove_export
    )
