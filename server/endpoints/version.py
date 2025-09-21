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
from fastapi import FastAPI
from pydantic import BaseModel

from ..core.package import APP_NAME
from ..core.package import APP_VERSION


class ServerInfo(BaseModel):
  name: str
  version: str


def create_version_endpoints(api: FastAPI):
  server_info = ServerInfo(
    name=APP_NAME,
    version=APP_VERSION,
  )

  @api.get('/', responses={
    200: {
      'content': {
        'application/json': {
          'example': server_info,
        },
      },
    },
  })
  async def get_server_info() -> ServerInfo:
    """
    Retrieve server information.

    This endpoint provides information about the server, including its
    name and version. This is useful for clients to know the server they
    are interacting with and to ensure compatibility with the API.
    """
    return server_info
