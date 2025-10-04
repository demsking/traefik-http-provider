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
from collections.abc import Mapping


def deep_merge(dict1: dict, dict2: dict) -> dict:
  """Recursively merge two dictionaries."""
  for key, value in dict2.items():
    if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, Mapping):
      # If both values are dicts, recursively merge them
      deep_merge(dict1[key], value)
    else:
      # Otherwise, overwrite the value in dict1
      dict1[key] = value

  return dict1
