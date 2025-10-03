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
import sqlite3
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any


from .logger import logger
from .merge import deep_merge

TrafikServiceConfig = dict[str, Any]


class ProviderConfigStore:
  def __init__(self, db_path: str) -> None:
    self.db_file = Path(db_path) / 'provider_configs.db'
    self.db_file.parent.mkdir(parents=True, exist_ok=True)
    self._init_db()

  def _init_db(self) -> None:
    with sqlite3.connect(self.db_file) as conn:
      conn.execute("PRAGMA journal_mode=WAL;")
      conn.execute("PRAGMA synchronous=NORMAL;")
      conn.execute("PRAGMA busy_timeout = 5000;")
      conn.execute(
        """
        CREATE TABLE IF NOT EXISTS provider_configs (
          service_id TEXT PRIMARY KEY,
          config TEXT NOT NULL,
          last_updated TEXT NOT NULL
        )
        """
      )
      conn.commit()

  def insert(self, service_id: str, config: TrafikServiceConfig) -> None:
    last_updated = datetime.utcnow().isoformat()

    logger.info(f"Inserting config for service {service_id} with last updated {last_updated}")

    with sqlite3.connect(self.db_file) as conn:
      conn.execute(
        """
        INSERT INTO provider_configs (service_id, config, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(service_id) DO UPDATE SET
          config = excluded.config,
          last_updated = excluded.last_updated
        """,
        (
          service_id,
          json.dumps(config),
          last_updated,
        ),
      )
      conn.commit()

  def get(self, service_id: str) -> TrafikServiceConfig | None:
    with sqlite3.connect(self.db_file) as conn:
      row = conn.execute(
        'SELECT service_id, config, last_updated FROM provider_configs WHERE service_id = ?',
        (service_id,),
      ).fetchone()

    if not row:
      return None

    return json.loads(row[1])

  def get_all(self) -> list[TrafikServiceConfig]:
    with sqlite3.connect(self.db_file) as conn:
      rows = conn.execute(
        'SELECT service_id, config, last_updated FROM provider_configs'
      ).fetchall()

    configs: list[TrafikServiceConfig] = []

    for row in rows:
      try:
        configs.append(json.loads(row[1]))
      except Exception as exc:
        logger.warning(f"Error parsing row {row}: {exc}")

    return configs

  def get_merged_config(self) -> TrafikServiceConfig:
    all_configs = self.get_all()
    merged: TrafikServiceConfig = {}

    logger.debug(f"Loaded {len(all_configs)} provider configurations from the database")

    for config in all_configs:
      merged = deep_merge(merged, config)

    return merged

  def delete_old_records(self, expiration_minutes: int) -> None:
    expiration_time = datetime.utcnow() - timedelta(minutes=expiration_minutes)

    logger.debug(f"Deleting records older than {expiration_time.isoformat()}")
    with sqlite3.connect(self.db_file) as conn:
      conn.execute(
        'DELETE FROM provider_configs WHERE last_updated < ?',
        (expiration_time.isoformat(),),
      )
      conn.commit()
