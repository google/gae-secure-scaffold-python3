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

import nox


nox.options.default_venv_backend = "venv"


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("flask", ["2", "3"])
def tests(session, flask):
    session.install("pytest")
    session.install(f"flask~={flask}.0")
    session.install(".")
    session.run("pytest", "--disable-warnings")
