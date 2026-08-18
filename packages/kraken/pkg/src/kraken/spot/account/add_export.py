"""`spot.account.add_export` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class AddExportResult(TypedDict):
  """The newly requested export report."""

  id: NotRequired[str]
  """Report ID, for use with `ExportStatus`/`RetrieveExport`/`RemoveExport`."""


validate_add_export = validator(AddExportResult)


class AddExport(RpcEndpoint):
  """`spot.account.add_export`."""

  async def add_export(
    self,
    *,
    report: Literal['trades', 'ledgers'],
    description: str,
    format: Literal['CSV', 'TSV'] | None = None,
    fields: str | None = None,
    starttm: int | None = None,
    endtm: int | None = None,
  ) -> AddExportResult:
    """Request an export of trades or ledgers. The export is asynchronous: this call returns a report ID, not the data itself -- poll `ExportStatus` and retrieve the finished file with `RetrieveExport`.

    **API Key Permissions Required:** `Data - Export data`

    Args:
      report: Type of data to export.
      description: Description for the export.
      format: File format to export.
      fields: Comma-delimited list of fields to include. Defaults to `all`. For `report: trades`: `ordertxid`, `time`, `ordertype`, `price`, `cost`, `fee`, `vol`, `margin`, `misc`, `ledgers`. For `report: ledgers`: `refid`, `time`, `type`, `subtype`, `aclass`, `asset`, `amount`, `fee`, `balance`, `wallet`.
      starttm: UNIX timestamp for report start time (defaults to the 1st of the current month).
      endtm: UNIX timestamp for report end time (defaults to now).

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/request-export-report)
    """
    data: dict = {
      'report': report,
      'description': description,
    }
    if format is not None:
      data['format'] = format
    if fields is not None:
      data['fields'] = fields
    if starttm is not None:
      data['starttm'] = starttm
    if endtm is not None:
      data['endtm'] = endtm

    return await self.authed_request(
      '/0/private/AddExport', data, validator=validate_add_export
    )
