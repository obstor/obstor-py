# -*- coding: utf-8 -*-
# Obstor Python Library for Amazon S3 Compatible Cloud Storage, (C)
# [2014] - [2025] MinIO, Inc.
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

"""Setup definitions."""

from __future__ import annotations

import re
from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent

# Read version from obstor/__init__.py
init_py = ROOT / "obstor" / "__init__.py"
version_match = re.search(
    r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    init_py.read_text(encoding="utf-8"),
    re.MULTILINE,
)
if not version_match:
    raise RuntimeError("Unable to find __version__ in obstor/__init__.py")
version = version_match.group(1)

# Long description
readme = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="obstor",
    version=version,
    description="Obstor Python SDK for Amazon S3 Compatible Cloud Storage",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="PGG, Inc.",
    author_email="oss@obstor.net",
    url="https://github.com/obstor/obstor-py",
    project_urls={
        "Source": "https://github.com/obstor/obstor-py",
        "Issues": "https://github.com/obstor/obstor-py/issues",
        "Changelog": "https://github.com/obstor/obstor-py/releases",
    },
    license="Apache-2.0",
    package_dir={"": "."},
    packages=find_packages(include=["obstor", "obstor.*"]),
    python_requires=">=3.10",
    install_requires=[
        "certifi",
        "urllib3",
        "argon2-cffi",
        "pycryptodome",
        "typing-extensions",
    ],
    include_package_data=True,
    package_data={
        "obstor": ["LICENSE", "README.md", "py.typed"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
