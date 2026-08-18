"""`spot.account.export_status` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class ExportReport(TypedDict):
  """The status of one requested export."""

  id: NotRequired[str]
  """Report ID."""
  descr: NotRequired[str]
  """Report description, as given to `AddExport`."""
  format: NotRequired[str]
  """File format of the report."""
  report: NotRequired[Literal['trades', 'ledgers']]
  """Report type."""
  subtype: NotRequired[str]
  """Report subtype."""
  status: NotRequired[Literal['Queued', 'Processing', 'Processed']]
  """Current status of the report."""
  error: NotRequired[
    Literal[
      'EExport:Internal error',
      'EExport:Unexpected error',
      'EExport:Canceled',
      'EExport:Deleted',
      'EExport:Exported size too big',
    ]
  ]
  """Error code, if the report failed."""
  flags: NotRequired[str]
  """Deprecated, no longer populated."""
  fields: NotRequired[str]
  """Comma-delimited list of fields included in the report."""
  createdtm: NotRequired[str]
  """UNIX timestamp of when the report was requested."""
  expiretm: NotRequired[str]
  """Deprecated, no longer populated."""
  starttm: NotRequired[str]
  """UNIX timestamp of when report processing began."""
  completedtm: NotRequired[str]
  """UNIX timestamp of when report processing finished."""
  datastarttm: NotRequired[str]
  """UNIX timestamp of the report data's start time."""
  dataendtm: NotRequired[str]
  """UNIX timestamp of the report data's end time."""
  aclass: NotRequired[str]
  """Deprecated -- superseded by `asset_classes`."""
  asset: NotRequired[str]
  """Asset filter applied to the report."""
  assets: NotRequired[str]
  """Plural sibling of `asset`, e.g. `"all"`. Confirmed present live alongside `asset` on the same response, not in upstream's own published field list -- possibly the newer replacement, unconfirmed against current docs."""
  asset_classes: NotRequired[list[str]]
  """Asset classes included in the report."""
  endtm: NotRequired[str]
  """Deprecated -- superseded by `dataendtm`."""
  delete: NotRequired[bool]
  """Whether the report is pending deletion."""


validate_export_status = validator(list[ExportReport])


class ExportStatus(RpcEndpoint):
  """`spot.account.export_status`."""

  async def export_status(
    self,
    report: Literal['trades', 'ledgers'],
  ) -> list[ExportReport]:
    """Get the status of requested data exports.

    **API Key Permissions Required:** `Data - Export data`

    Args:
      report: Type of reports to inquire about.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-export-report-status)
    """
    data: dict = {
      'report': report,
    }

    return await self.authed_request(
      '/0/private/ExportStatus', data, validator=validate_export_status
    )
