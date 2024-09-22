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
import json
import sqlite3
from datetime import datetime
from datetime import timedelta

from oremi_core.vars import getenv

from .logger import logger
from .merge import deep_merge


def get_dbname() -> str:
  return getenv('PROVIDERS_DATABASE', default='providers.db')


def get_db_connection(dbname: str | None = None):
  connection = sqlite3.connect(dbname or get_dbname())
  connection.row_factory = sqlite3.Row

  return connection


def initialize_db() -> None:
  dbname = get_dbname()

  logger.info(f'Initializing database {dbname}')
  connection = get_db_connection(dbname)
  connection.execute('''
    CREATE TABLE IF NOT EXISTS providers (
      sid TEXT PRIMARY KEY,
      config TEXT NOT NULL,
      lastUpdated DATETIME NOT NULL
    )
  ''')
  connection.commit()
  connection.close()


def insert_provider_config(service_id: str, config: dict) -> None:
  connection = get_db_connection()
  now = datetime.utcnow()

  try:
    connection.execute(
      '''
      INSERT OR REPLACE INTO providers (sid, config, lastUpdated)
      VALUES (?, ?, ?)
      ''',
      (service_id, json.dumps(config), now)
    )
    connection.commit()
  finally:
    connection.close()


def get_merged_config() -> dict:
  connection = get_db_connection()

  try:
    cursor = connection.execute('SELECT config FROM providers')
    providers = cursor.fetchall()
    merged_data = {}

    for provider in providers:
      config = json.loads(provider['config'])
      merged_data = deep_merge(merged_data, config)

    return merged_data
  finally:
    connection.close()


def delete_old_records(expiration_minutes: int) -> None:
  connection = get_db_connection()

  try:
    expiration_time = datetime.utcnow() - timedelta(minutes=expiration_minutes)
    connection.execute(
      '''
      DELETE FROM providers WHERE lastUpdated < ?
      ''',
      (expiration_time,)
    )
    connection.commit()
  finally:
    connection.close()
