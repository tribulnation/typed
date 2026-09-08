"""Signed query strings must not escape through HTTP failure diagnostics."""

import traceback
from unittest.mock import AsyncMock

import httpx
import pytest

from typed_core.exceptions import NetworkError
from typed_core.http import HttpClient


@pytest.mark.parametrize('error_type', [httpx.ConnectError, httpx.ReadTimeout])
@pytest.mark.asyncio
async def test_network_error_hides_url_credentials(
  monkeypatch: pytest.MonkeyPatch, error_type: type[httpx.HTTPError],
):
  """The message and ordinary traceback omit URL credentials and transport text."""
  url = 'https://username:password@example.invalid:8443/api/orders?signature=secret#token'
  error = error_type(f'Failed at {url}')
  request = AsyncMock(side_effect=error)
  monkeypatch.setattr(httpx.AsyncClient, 'request', request)
  params = {'api_key': 'query-secret'}

  async with HttpClient() as client:
    with pytest.raises(NetworkError) as caught:
      await client.request('GET', url, params=params)

  assert caught.value.args == (
    'Error sending request to GET https://example.invalid:8443/api/orders '
    f'({error_type.__name__})',
  )
  rendered = ''.join(traceback.format_exception(caught.value))
  for credential in ['username', 'password', 'signature', 'secret', 'token']:
    assert credential not in str(caught.value)
    assert credential not in rendered
  assert caught.value.__suppress_context__
  request.assert_awaited_once()
  assert request.call_args.args == ('GET', url)
  assert request.call_args.kwargs['params'] == {'api_key': 'query-secret'}
