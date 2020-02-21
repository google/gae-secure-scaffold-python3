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

# Variables with all-capitals will be added to the Flask app's configuration.

# See https://github.com/GoogleCloudPlatform/flask-talisman for details on
# configuring CSP.

# Strict policy, allows using nonce in templates to load JS and CSS assets.
CSP_POLICY = {
    "default-src": "'none'",
    "script-src": "",
    "style-src": "",
}
CSP_POLICY_NONCE_IN = ["script-src", "style-src"]
