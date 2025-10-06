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
from datetime import timedelta
from functools import reduce
from typing import Any

import redis

from .config import EXPIRATION_MINUTES
from .config import REDIS_DB
from .config import REDIS_HOST
from .config import REDIS_PASSWORD
from .config import REDIS_PORT
from .merge import deep_merge

TraefikServiceConfig = dict[str, Any]


class ProviderStore:
  def __init__(self, logger: logging.Logger) -> None:
    self.logger = logger
    self.client = redis.Redis(
      host=REDIS_HOST,
      port=REDIS_PORT,
      db=REDIS_DB,
      password=REDIS_PASSWORD,
      decode_responses=True,
      socket_timeout=5,
      socket_connect_timeout=5,
      health_check_interval=30,
    )

  def insert(self, service_id: str, provider_config: TraefikServiceConfig) -> None:
    key = f"provider:{service_id}"
    value = json.dumps(provider_config)

    try:
      self.client.setex(key, timedelta(minutes=EXPIRATION_MINUTES), value)
    except redis.RedisError as exc:
      self.logger.error(f"Error inserting provider config for {service_id}: {exc}")
      raise

  def get(self, service_id: str) -> TraefikServiceConfig | None:
    key = f"provider:{service_id}"

    try:
      data = self.client.get(key)

      return json.loads(data) if data else None
    except redis.RedisError as exc:
      self.logger.error(f"Error retrieving provider config for {service_id}: {exc}")
      return None

  def get_all(self) -> list[TraefikServiceConfig]:
    try:
      keys = self.client.keys('provider:*')
      configs: list[TraefikServiceConfig] = []

      for key in keys:
        data = self.client.get(key)

        if data:
          try:
            configs.append(json.loads(data))
          except Exception as exc:
            self.logger.warning(f"Error parsing data for {key}: {exc}")
            self.client.delete(key)
      return configs
    except redis.RedisError as exc:
      self.logger.error(f"Error retrieving all provider configs: {exc}")
      return []

  def get_merged_config(self) -> TraefikServiceConfig:
    configs = self.get_all()

    return reduce( lambda acc, config: deep_merge(acc, config), configs, {} )
