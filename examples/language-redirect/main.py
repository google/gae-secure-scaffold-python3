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

import securescaffold
import securescaffold.views


app = securescaffold.create_app(__name__)

# The only route redirects visitors to /intl/LANG/ depending on the
# Accept-Language header.
app.add_url_rule("/", "lang_redirect", securescaffold.views.lang_redirect)
app.config["LOCALES"] = ["en", "fr"]
app.config["LOCALES_REDIRECT_TO"] = "/intl/{locale}/"
