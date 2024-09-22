from fastapi.testclient import TestClient

from server import api


client = TestClient(api, backend='asyncio')


def test_register_service_config_api_config__service_id__post(service2):
  """Register Provider"""
  path = '/api/config/service2'
  response = client.post(path, json=service2)

  assert response.status_code == 200
  assert response.headers['Content-Type'] == 'application/json'
  assert response.json() == {'message': 'Provider registered successfully'}
