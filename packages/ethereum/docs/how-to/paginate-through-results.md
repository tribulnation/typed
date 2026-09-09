# Pagination Boundaries

The balance helpers perform point reads; this package exposes no `_paged` methods
or automatic historical scan. Repeated balance calls are not a history backfill.

For additional node operations, use `client.w3` with the chosen provider's supported
RPC surface. Your application must select ranges and handle that provider's limits;
this wrapper does not promise complete historical data or automatic pagination.
