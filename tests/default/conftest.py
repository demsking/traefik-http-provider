import pytest

from server.core.database import initialize_db


# Fixture to run before all tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
  initialize_db()  # Initialize the database before running tests
  yield


@pytest.fixture
def service1():
  return {
    "http": {
      "routers": {
        "router-service1": {
          "rule": "Host(`example.com`)",
          "service": "service1",
          "entryPoints": [
            "web"
          ]
        }
      },
      "services": {
        "service1": {
          "loadBalancer": {
            "servers": [
              {
                "url": "http://service1:8080"
              }
            ]
          }
        }
      }
    }
  }
