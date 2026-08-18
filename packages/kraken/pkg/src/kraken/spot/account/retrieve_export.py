"""`spot.account.retrieve_export` -- raw binary response, not the `{error, result}` envelope."""

from ...core.endpoint.rpc import RpcEndpoint


class RetrieveExport(RpcEndpoint):
  """`spot.account.retrieve_export`."""

  async def retrieve_export(self, id: str) -> bytes:
    """Retrieve a processed data export. Unlike every other Account Data endpoint, the response is not the standard `{error, result}` JSON envelope -- it is the raw export file itself.

    **API Key Permissions Required:** `Data - Export data`

    Args:
      id: Report ID to retrieve.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/retrieve-data-export)
    """
    data: dict = {
      'id': id,
    }

    return await self.authed_raw_request('/0/private/RetrieveExport', data)
