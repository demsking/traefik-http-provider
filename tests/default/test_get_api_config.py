from fastapi.testclient import TestClient

from server import api


client = TestClient(api, backend='asyncio')


def test_get_traefik_config_api_config_get():
  """Get Traefik Config"""
  path = '/api/config'
  response = client.get(path)

  assert response.status_code == 200
  assert response.headers['Content-Type'] == 'application/json'
  assert response.json() is not None

