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
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from functools import reduce
from pathlib import Path
from typing import Any

from .logger import logger
from .merge import deep_merge

TrafikServiceConfig = dict[str, Any]


@dataclass
class ProviderConfig:
  service_id: str
  config: TrafikServiceConfig
  last_updated: str

  @staticmethod
  def from_dict(data: dict[str, Any]) -> 'ProviderConfig':
    return ProviderConfig(
      service_id=data['service_id'],
      config=data['config'],
      last_updated=data['last_updated']
    )

  def to_dict(self) -> TrafikServiceConfig:
    return asdict(self)


class ProviderConfigStore:
  def __init__(self, directory: str) -> None:
    self.data_directory = Path(directory)

  def insert(self, provider_config: ProviderConfig) -> None:
    file_path = self.data_directory / f'{provider_config.service_id}.json'

    with file_path.open('w', encoding='utf-8') as file:
      json.dump(provider_config.to_dict(), file, indent=2)

  def get(self, service_id: str) -> ProviderConfig | None:
    file_path = self.data_directory / f'{service_id}.json'

    if not file_path.exists():
      return None

    with file_path.open('r', encoding='utf-8') as file:
      data = json.load(file)

    return ProviderConfig.from_dict(data)

  def get_all(self) -> list[ProviderConfig]:
    configs = []

    for file_path in self.data_directory.glob('*.json'):
      with file_path.open('r', encoding='utf-8') as file:
        data = json.load(file)

      try:
        configs.append(ProviderConfig.from_dict(data))
      except Exception as exception:
        logger.error(f'Error while parsing {file_path}: {exception}')
        file_path.unlink()

    return configs

  def get_merged_config(self) -> TrafikServiceConfig:
    all_configs = self.get_all()

    return reduce(
      lambda acc, cfg: deep_merge(acc, cfg.config),
      all_configs,
      {}
    )

  def delete_old_records(self, expiration_minutes: int) -> None:
    expiration_time = datetime.utcnow() - timedelta(minutes=expiration_minutes)

    for file_path in self.data_directory.glob('*.json'):
      with file_path.open('r', encoding='utf-8') as file:
        data = json.load(file)

      last_updated = datetime.fromisoformat(data['last_updated'])

      if last_updated < expiration_time:
        file_path.unlink()
