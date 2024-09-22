import pytest
from fastapi.testclient import TestClient

from server import api


client = TestClient(api, backend='asyncio')


@pytest.fixture
def service2(register_provider_api_provider__service_id__post_payload):
  return register_provider_api_provider__service_id__post_payload


def test_register_provider_api_provider__service_id__post(service2):
  """Register Provider"""
  path = '/api/provider/service2'
  response = client.post(path, json=service2)

  assert response.status_code == 200
  assert response.headers['Content-Type'] == 'application/json'
  assert response.json() == {'message': 'Provider registered successfully'}


def test_integration(service1, service2):
  client.post('/api/provider/service1', json=service1)
  client.post('/api/provider/service2', json=service2)

  response = client.get('/api/provider')

  assert response.status_code == 200
  assert response.headers['Content-Type'] == 'application/json'
  assert response.json() == {
    'http': {
      'routers': {
        'router-service1': {
          'entryPoints': [
            'web',
          ],
          'rule': 'Host(`example.com`)',
          'service': 'service1',
        },
        'router-service2': {
            'entryPoints': [
              'web',
            ],
            'rule': 'Host(`example.com`)',
            'service': 'service2',
        },
      },
      'services': {
        'service1': {
          'loadBalancer': {
            'servers': [
              {
                'url': 'http://service1:8080',
              },
            ],
          },
        },
        'service2': {
          'loadBalancer': {
            'servers': [
              {
                'url': 'http://service2:8080',
              },
            ],
          },
        },
      },
    },
  }

