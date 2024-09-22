# Copyright 2024 Sébastien Demanou. All Rights Reserved.
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
import os
import sqlite3
from typing import Any

from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from oremi_core.vars import getenv
from pydantic import BaseModel

from .core.database import delete_old_records
from .core.database import get_merged_config
from .core.database import insert_provider_config
from .core.logger import logger
from .core.package import APP_NAME
from .core.package import APP_VERSION


HTTP_AGENT = f'{APP_NAME}/{APP_VERSION}'
SERVICE_TITLE = 'Traefik HTTP Provider'
DATABASE_NAME = getenv('PROVIDERS_DATABASE', default='providers.db')
EXPIRATION_MINUTES = getenv('EXPIRATION_MINUTES', expected_type=int, default=30)
TrafikServiceConfig = dict[str, Any]
TrafikConfig = dict[str, Any]

_current_dir = os.path.dirname(os.path.abspath(__file__))
_readme_path = os.path.realpath(
  os.path.join(_current_dir, '..', 'DOCUMENTATION.md'),
)


with open(_readme_path, 'r', encoding='utf-8') as file:
  SERVICE_DESCRIPTION = file.read()


api = FastAPI(
  docs_url=None,
  redoc_url='/docs',
  title=SERVICE_TITLE,
  version=APP_VERSION,
  description=SERVICE_DESCRIPTION,
  license_info={
    'name': 'Apache 2.0',
    'url': 'http://www.apache.org/licenses/LICENSE-2.0.html',
  },
)


class SuccessResponse(BaseModel):
  message: str


@api.post('/api/provider/{service_id}', responses={
  200: {'description': 'Provider registered successfully'},
  400: {'description': 'Invalid input data'},
  500: {'description': 'Internal database error'},
})
async def register_provider(
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

  The configuration is stored or replaced in the SQLite database with a
  timestamp indicating the last update.
  """
  try:
    insert_provider_config(service_id, config)
  except sqlite3.Error as exception:
    raise HTTPException(status_code=500, detail='Database error') from exception

  return {'message': 'Provider registered successfully'}


@api.get('/api/provider', responses={
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
  500: {'description': 'Internal database error'},
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
    logger.info('Cleaning outdated data')
    delete_old_records(EXPIRATION_MINUTES)
    logger.info('Old records cleanup complete. Proceeding to fetch providers.')

    merged_data = get_merged_config()
  except sqlite3.Error as exception:
    raise HTTPException(status_code=500, detail='Database error') from exception

  return merged_data
