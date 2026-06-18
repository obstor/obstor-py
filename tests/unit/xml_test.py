# -*- coding: utf-8 -*-
# Obstor Python Library for Amazon S3 Compatible Cloud Storage, (C)
# [2021] - [2025] PGG, Inc.
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

from unittest import TestCase

from obstor.xml import fromstring

_BILLION_LAUGHS = (
    '<?xml version="1.0"?>'
    "<!DOCTYPE lolz ["
    ' <!ENTITY lol "lol">'
    ' <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
    ' <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
    "]>"
    "<lolz>&lol3;</lolz>"
)

_NORMAL = (
    '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    "<Name>bucket</Name></ListBucketResult>"
)


class XmlTest(TestCase):
    def test_rejects_doctype_entity_bomb(self):
        # A DTD/DOCTYPE in an endpoint-controlled body DoS must be refused
        with self.assertRaises(ValueError):
            fromstring(_BILLION_LAUGHS)
        with self.assertRaises(ValueError):
            fromstring(_BILLION_LAUGHS.encode())

    def test_parses_normal_s3_xml(self):
        element = fromstring(_NORMAL)
        self.assertTrue(element.tag.endswith("ListBucketResult"))
        # Bytes input parses identically.
        self.assertEqual(fromstring(_NORMAL.encode()).tag, element.tag)
