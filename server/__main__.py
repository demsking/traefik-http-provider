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
import multiprocessing
import os

import uvicorn.config

from server.core.logger import logger
from server.core.package import APP_NAME
from server.core.package import APP_VERSION


def get_log_config():
  current_dir = os.path.dirname(os.path.abspath(__file__))
  config_filename = os.path.join(current_dir, 'log-config.json')

  with open(config_filename, 'r', encoding='utf-8') as file:
    return json.load(file)


def main():
  verbose = logger.isEnabledFor(logging.DEBUG)
  workers = int(os.getenv('WORKERS') or '0') or multiprocessing.cpu_count()
  log_config = get_log_config() if not verbose else uvicorn.config.LOGGING_CONFIG

  logger.info(f'Starting {APP_NAME}/{APP_VERSION}')
  logger.info(f'Log level: {"DEBUG" if verbose else "INFO"}')

  uvicorn.run(
    app='server:api',
    host='0.0.0.0',
    port=6116,
    workers=workers if not verbose else 1,
    server_header=False,
    use_colors=True,
    proxy_headers=True,
    log_level='info',
    log_config=log_config,
  )


if __name__ == '__main__':
  main()
