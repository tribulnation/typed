"""`spot.account.retrieve_export` -- hand-written, not generated.

Its 2xx response is a raw binary zip archive (`Content-Type: application/zip`), not a
JSON-schema-describable value -- the universal `Generator`'s `rpc_endpoint` (design §7)
has no way to express "no schema, but the return type is `bytes`," so this leaf keeps a
real, hand-written module instead (`endpoint.json` declares `surface: {"kind":
"handwritten", ...}`, and `Generator.skip_endpoint`'s default respects it). Everything
else about this endpoint -- its resolved core (`RpcEndpoint`, `spot/`'s subtree core),
signing, path -- is identical to a generated leaf; only the final `bytes` return and the
direct `self.client.authed_raw_request(...)` call (bypassing the unified `.request()`
verb, which has no way to skip response-schema validation for a body that isn't JSON at
all) are hand-written.
"""

from ...core.endpoint.rpc import RpcEndpoint


class RetrieveExport(RpcEndpoint):
  """`spot.account.retrieve_export`."""

  async def retrieve_export(self, id: str, *, validate: bool | None = None) -> bytes:
    """Retrieve a processed data export. Unlike every other Account Data endpoint, the response is not the standard `{error, result}` JSON envelope -- it is the raw export file itself.

    **API Key Permissions Required:** `Data - Export data`

    Args:
      id: Report ID to retrieve.
      validate: Accepted for signature uniformity with every other generated `rpc`
        method (S8); has no effect -- there is no schema to validate a raw binary body
        against.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/retrieve-data-export)
    """
    data: dict = {
      'id': id,
    }

    return await self.client.authed_raw_request(
      '/0/private/RetrieveExport', data, validate=validate
    )
