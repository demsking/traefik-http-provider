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
import json
import logging
import os

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.api import parse_path
from .core.logger import create_logger
from .core.config import EXPIRATION_MINUTES
from .core.config import LOG_FILE
from .core.config import LOG_LEVEL
from .core.config import REDIS_DB
from .core.config import REDIS_HOST
from .core.config import REDIS_PORT
from .core.config import REDIS_PASSWORD
from .core.config import ROOT_PATH
from .core.package import APP_NAME
from .core.package import APP_VERSION
from .endpoints.config import create_config_endpoints
from .endpoints.docs import create_docs_endpoints
from .endpoints.version import create_version_endpoints


HTTP_AGENT = f'{APP_NAME}/{APP_VERSION}'
SERVICE_TITLE = 'Traefik HTTP Provider'

_current_dir = os.path.dirname(os.path.abspath(__file__))
_readme_path = os.path.realpath(os.path.join(_current_dir, '..', 'DOCUMENTATION.md'))

logger = create_logger()

with open(_readme_path, 'r', encoding='utf-8') as file:
  SERVICE_DESCRIPTION = file.read()

BASE_PATH = parse_path('/api')


@asynccontextmanager
async def lifespan(app: FastAPI):
  # execute the app lifespan at the start of the context manager and at the end

  logger.info(f'Starting {APP_NAME}/{APP_VERSION}')
  logger.info(f'Log Level: {LOG_LEVEL}')
  logger.info(f'Log File Path: {LOG_FILE or None}')
  logger.info(f'Server Root Path: {ROOT_PATH}')
  logger.info(f'API Base Path: {BASE_PATH}')
  logger.info(f'Config Expiration Minutes: {EXPIRATION_MINUTES}')
  logger.info(f'Redis DNS: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')
  logger.info(f'Redis Password: {"****" if REDIS_PASSWORD else None}')
  yield


api = FastAPI(
  docs_url=None,
  redoc_url=None,
  lifespan=lifespan,
  title=SERVICE_TITLE,
  version=APP_VERSION,
  description=SERVICE_DESCRIPTION,
  root_path=BASE_PATH,
  servers=[{'url': BASE_PATH}],
  license_info={
    'name': 'Apache 2.0',
    'url': 'http://www.apache.org/licenses/LICENSE-2.0.html',
  },
)

create_config_endpoints(api, logger)
create_docs_endpoints(api)
create_version_endpoints(api)


def get_log_config() -> dict:
  current_dir = os.path.dirname(os.path.abspath(__file__))
  config_filename = os.path.join(current_dir, 'log-config.json')

  with open(config_filename, 'r', encoding='utf-8') as file:
    return json.load(file)


def main() -> None:
  verbose = logger.isEnabledFor(logging.DEBUG)
  log_config = get_log_config() if not verbose else uvicorn.config.LOGGING_CONFIG

  uvicorn.run(
    app=api,
    host='0.0.0.0',
    port=6116,
    server_header=False,
    use_colors=True,
    proxy_headers=True,
    log_level='info',
    log_config=log_config,
  )
