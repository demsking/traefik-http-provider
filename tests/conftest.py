# pylint: disable=wildcard-import,unused-wildcard-import,invalid-name,line-too-long
import pytest


@pytest.fixture
def register_service_config_api_config__service_id__post_payload():
  return {
    "http": {
      "routers": {
        "router-service2": {
          "rule": "Host(`example.com`)",
          "service": "service2",
          "entryPoints": [
            "web"
          ]
        }
      },
      "services": {
        "service2": {
          "loadBalancer": {
            "servers": [
              {
                "url": "http://service2:8080"
              }
            ]
          }
        }
      }
    }
  }


@pytest.fixture
def service_id():
  return None

