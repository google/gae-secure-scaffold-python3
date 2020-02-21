# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Validates user input when using cookiecutter to start a project."""
import re


project = """{{ cookiecutter.project }}"""

if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", project):
    print("ERROR: project must be lower-case letters, numbers and dashes and must start with a letter")

    raise SystemExit(1)
