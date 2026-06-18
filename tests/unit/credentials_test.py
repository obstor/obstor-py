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

import os
from unittest import TestCase

from obstor.credentials.providers import (AWSConfigProvider, ChainedProvider,
                                         EnvAWSProvider, EnvObstorProvider,
                                         StaticProvider)

CREDENTIALS_SAMPLE = "tests/unit/credentials.sample"
CREDENTIALS_EMPTY = "tests/unit/credentials.empty"


class CredentialsTest(TestCase):
    def test_credentials_get(self):
        provider = StaticProvider(
            "Q3AM3UQ867SPQQA43P2F",
            "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
        )
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "Q3AM3UQ867SPQQA43P2F")
        self.assertEqual(creds.secret_key,
                         "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG")
        self.assertEqual(creds.session_token, None)


class ChainedProviderTest(TestCase):
    def test_chain_retrieve(self):
        # clear environment
        os.environ.clear()
        # prepare env for env_aws provider
        os.environ["AWS_ACCESS_KEY_ID"] = "access_aws"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "secret_aws"
        os.environ["AWS_SESSION_TOKEN"] = "token_aws"
        # prepare env for env_obstor
        os.environ["OBSTOR_ACCESS_KEY"] = "access_obstor"
        os.environ["OBSTOR_SECRET_KEY"] = "secret_obstor"
        # create chain provider with env_aws and env_obstor providers

        provider = ChainedProvider(
            [
                EnvAWSProvider(), EnvObstorProvider(),
            ]
        )
        # retrieve provider (env_aws) has priority
        creds = provider.retrieve()
        # assert provider credentials
        self.assertEqual(creds.access_key, "access_aws")
        self.assertEqual(creds.secret_key, "secret_aws")
        self.assertEqual(creds.session_token, "token_aws")

    def test_chain_retrieve_failed_provider(self):
        # clear environment
        os.environ.clear()
        # prepare env for env_obstor
        os.environ["OBSTOR_ACCESS_KEY"] = "access_obstor"
        os.environ["OBSTOR_SECRET_KEY"] = "secret_obstor"
        # create chain provider with env_aws and env_obstor providers

        provider = ChainedProvider(
            [
                EnvAWSProvider(), EnvObstorProvider(),
            ]
        )
        # retrieve provider: (env_obstor) will be retrieved
        creds = provider.retrieve()
        # assert provider credentials
        self.assertEqual(creds.access_key, "access_obstor")
        self.assertEqual(creds.secret_key, "secret_obstor")
        self.assertEqual(creds.session_token, None)


class EnvAWSProviderTest(TestCase):
    def test_env_aws_retrieve(self):
        os.environ.clear()
        os.environ["AWS_ACCESS_KEY_ID"] = "access"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "secret"
        os.environ["AWS_SESSION_TOKEN"] = "token"
        provider = EnvAWSProvider()
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "access")
        self.assertEqual(creds.secret_key, "secret")
        self.assertEqual(creds.session_token, "token")

    def test_env_aws_retrieve_no_token(self):
        os.environ.clear()
        os.environ["AWS_ACCESS_KEY_ID"] = "access"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "secret"
        provider = EnvAWSProvider()
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "access")
        self.assertEqual(creds.secret_key, "secret")
        self.assertEqual(creds.session_token, None)


class EnvObstorTest(TestCase):
    def test_env_obstor_retrieve(self):
        os.environ.clear()
        os.environ['OBSTOR_ACCESS_KEY'] = "access"
        os.environ["OBSTOR_SECRET_KEY"] = "secret"
        provider = EnvObstorProvider()
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "access")
        self.assertEqual(creds.secret_key, "secret")
        self.assertEqual(creds.session_token, None)


class AWSConfigProviderTest(TestCase):
    def test_file_aws(self):
        os.environ.clear()
        provider = AWSConfigProvider(CREDENTIALS_SAMPLE)
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "accessKey")
        self.assertEqual(creds.secret_key, "secret")
        self.assertEqual(creds.session_token, "token")

    def test_file_aws_from_env(self):
        os.environ.clear()
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = (
            CREDENTIALS_SAMPLE
        )
        provider = AWSConfigProvider()
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "accessKey")
        self.assertEqual(creds.secret_key, "secret")
        self.assertEqual(creds.session_token, "token")

    def test_file_aws_env_profile(self):
        os.environ.clear()
        os.environ["AWS_PROFILE"] = "no_token"
        provider = AWSConfigProvider(CREDENTIALS_SAMPLE)
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "accessKey")
        self.assertEqual(creds.secret_key, "secret")
        self.assertEqual(creds.session_token, None)

    def test_file_aws_arg_profile(self):
        os.environ.clear()
        provider = AWSConfigProvider(
            CREDENTIALS_SAMPLE,
            "no_token",
        )
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "accessKey")
        self.assertEqual(creds.secret_key, "secret")
        self.assertEqual(creds.session_token, None)

    def test_file_aws_no_creds(self):
        os.environ.clear()
        provider = AWSConfigProvider(
            CREDENTIALS_EMPTY,
            "no_token",
        )
        try:
            provider.retrieve()
        except ValueError:
            pass


class StaticProviderTest(TestCase):
    def test_static_credentials(self):
        provider = StaticProvider("UXHW", "SECRET")
        creds = provider.retrieve()
        self.assertEqual(creds.access_key, "UXHW")
        self.assertEqual(creds.secret_key, "SECRET")
        self.assertEqual(creds.session_token, None)
