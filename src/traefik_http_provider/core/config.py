# Copyright 2025 Sébastien Demanou. All Rights Reserved.
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
from oremi_core.vars import getenv


ROOT_PATH = getenv('ROOT_PATH', default='/')
"""The root path for the API, which defines the base URL path for all routes. Default is '/'."""

LOG_FILE = getenv('LOG_FILE', default='')
"""Path to the log file where application logs will be stored. If left empty, logs may be directed
to the console by default."""

LOG_LEVEL: str = getenv(
  'LOG_LEVEL', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
)
"""The log level used to control the verbosity of application logs."""

EXPIRATION_MINUTES: int = getenv('EXPIRATION_MINUTES', expected_type=int, default=10)
"""Specifies the time window (in minutes) for filtering provider configurations. Default is 10."""

REDIS_HOST: str = getenv('REDIS_HOST')
"""Redis hostname or service name. Example: 'redis'."""

REDIS_PORT: int = getenv('REDIS_PORT', expected_type=int, default=6379)
"""Redis port number. Default is 6379."""

REDIS_DB: int = getenv('REDIS_DB', expected_type=int, default=0)
"""Redis database index to use. Default is 0."""

REDIS_PASSWORD: str = getenv('REDIS_PASSWORD', default='')
"""Optional Redis password for authenticated connections. Default is empty."""
