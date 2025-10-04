# Copyright 2024-2025 Sébastien Demanou. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import logging

from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

from ..core.store import ProviderStore
from ..core.store import TraefikServiceConfig


class SuccessResponse(BaseModel):
  message: str


def create_config_endpoints(api: FastAPI, logger: logging.Logger) -> None:
  _store = ProviderStore(logger)

  @api.post('/config/{service_id}', responses={
    200: {'description': 'Provider registered successfully'},
    400: {'description': 'Invalid input data'},
    500: {'description': 'Internal Server Error'},
  })
  async def register_service_config(
    service_id: str,
    config: TraefikServiceConfig = Body(..., examples=[
      {
        'http': {
          'routers': {
            'router-service2': {
              'rule': 'Host(`example.com`)',
              'service': 'service2',
              'entryPoints': ['web'],
            },
          },
          'services': {
            'service2': {
              'loadBalancer': {
                'servers': [{'url': 'http://service2:8080'}],
              },
            },
          },
        },
      },
    ]),
  ) -> SuccessResponse:
    """
    Register or update a provider's Traefik configuration in Redis.
    """
    try:
      _store.insert(service_id, config)
    except Exception as exc:
      logger.error(f"Error registering provider config: {exc}")
      raise HTTPException(
        status_code=500,
        detail=f"Failed to register provider config for service_id '{service_id}': {exc}",
      ) from exc

    return {'message': 'Provider registered successfully'}

  @api.get('/config', responses={
    200: {
      'description': 'Merged provider configurations',
      'content': {
        'application/json': {
          'example': {
            'http': {
              'routers': {
                'router-service1': {
                  'rule': 'Host(`service1.example.com`)',
                  'service': 'service1',
                  'entryPoints': ['web']
                },
                'router-service2': {
                  'rule': 'Host(`service2.example.com`)',
                  'service': 'service2',
                  'entryPoints': ['web']
                }
              },
              'services': {
                'service1': {
                  'loadBalancer': {'servers': [{'url': 'http://service1:8080'}]}
                },
                'service2': {
                  'loadBalancer': {'servers': [{'url': 'http://service2:8080'}]}
                }
              }
            }
          }
        }
      }
    },
    500: {'description': 'Internal Server Error'},
  })
  async def get_traefik_config() -> TraefikServiceConfig:
    """
    Retrieve and merge provider configurations stored in Redis.
    Expired configurations are automatically handled via Redis TTL.
    """
    try:
      logger.debug('Fetching merged provider configuration...')
      merged_data = _store.get_merged_config()
    except Exception as exc:
      logger.error(f"Error retrieving merged config: {exc}")
      raise HTTPException(
        status_code=500,
        detail=f"Failed to retrieve merged provider configurations: {exc}",
      ) from exc

    return merged_data
