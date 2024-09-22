from fastapi.testclient import TestClient

from server import api


client = TestClient(api, backend='asyncio')


def test_get_merged_providers_api_provider_get():
  """Get Merged Providers"""
  path = '/api/provider'
  response = client.get(path)

  assert response.status_code == 200
  assert response.headers['Content-Type'] == 'application/json'
  assert response.json() is not None

