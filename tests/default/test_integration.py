from fastapi.testclient import TestClient

from server import api


client = TestClient(api, backend='asyncio')



def test_integration(service1, service2):
  client.post('/api/config/service1', json=service1)
  client.post('/api/config/service2', json=service2)

  response = client.get('/api/config')

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
