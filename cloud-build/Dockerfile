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

# Based on https://github.com/dhermes/python-multi
FROM gcr.io/google.com/cloudsdktool/cloud-sdk:latest

ENV DEBIAN_FRONTEND noninteractive

# Install dependencies.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    git \
    ca-certificates \
    libffi-dev \
  && apt-get clean autoclean \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && rm -f /var/cache/apt/archives/*.deb

# Install ``pyenv``.
RUN git clone https://github.com/pyenv/pyenv /root/.pyenv

# Install the desired versions of Python.
RUN for PYTHON_VERSION in 3.7.6 3.8.2; do \
  set -ex \
    && /root/.pyenv/bin/pyenv install ${PYTHON_VERSION} \
    && /root/.pyenv/versions/${PYTHON_VERSION}/bin/python -m pip install --upgrade pip \
  ; done

# Add to PATH, in order of lowest precedence to highest.
ENV PATH /root/.pyenv/versions/3.7.6/bin:${PATH}
ENV PATH /root/.pyenv/versions/3.8.2/bin:${PATH}

CMD ["python3.8"]
