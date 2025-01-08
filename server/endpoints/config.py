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
from datetime import datetime
from typing import Any

from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from oremi_core.vars import getenv
from pydantic import BaseModel

from ..core.logger import logger
from ..core.store import ProviderConfig
from ..core.store import ProviderConfigStore
from ..core.store import TrafikServiceConfig

TrafikConfig = dict[str, Any]


class SuccessResponse(BaseModel):
  message: str


def create_config_endpoints(api: FastAPI) -> None:
  DATA_PATH = getenv('DATA_PATH')
  EXPIRATION_MINUTES = getenv('EXPIRATION_MINUTES', expected_type=int, default=30)

  _store = ProviderConfigStore(DATA_PATH)

  @api.post('/config/{service_id}', responses={
    200: {'description': 'Provider registered successfully'},
    400: {'description': 'Invalid input data'},
    500: {'description': 'Internal Server Error'},
  })
  async def register_service_config(
    service_id: str,
    config: TrafikServiceConfig = Body(..., examples=[
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
                'servers': [
                  {
                    'url': 'http://service2:8080',
                  },
                ],
              },
            },
          },
        },
      },
    ]),
  ) -> SuccessResponse:
    """
    Register or update a provider's Traefik configuration.

    This endpoint allows an external service to register or update its Traefik
    HTTP provider configuration.

    The configuration is stored or replaced in the providers data directory with
    a timestamp indicating the last update.
    """
    try:
      current_date = str(datetime.utcnow())
      data = ProviderConfig(service_id, config, last_updated=current_date)

      _store.insert(data)
    except Exception as exception:
      raise HTTPException(status_code=500) from exception

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
                  'loadBalancer': {
                    'servers': [
                      {
                        'url': 'http://service1:8080'
                      }
                    ]
                  }
                },
                'service2': {
                  'loadBalancer': {
                    'servers': [
                      {
                        'url': 'http://service2:8080'
                      }
                    ]
                  }
                }
              }
            }
          },
        },
      },
    },
    500: {'description': 'Internal Server Error'},
  })
  async def get_traefik_config() -> TrafikConfig:
    """
    Retrieve and merge provider configurations updated within the last X minutes.

    This endpoint retrieves all provider configurations that were updated within
    the last number of minutes specified by the `EXPIRATION_MINUTES` environment
    variable. The default is 30 minutes.
    The configurations are merged into a single JSON object.
    """
    try:
      logger.debug('Cleaning outdated data')
      _store.delete_old_records(EXPIRATION_MINUTES)
      logger.debug('Old records cleanup complete. Proceeding to fetch providers.')

      merged_data = _store.get_merged_config()
    except Exception as exception:
      raise HTTPException(status_code=500) from exception

    return merged_data
