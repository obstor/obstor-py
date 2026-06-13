# -*- coding: utf-8 -*-
# Obstor Python Library for Amazon S3 Compatible Cloud Storage,
# (C) [2024] - [2026] MinIO, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Upload to Obstor over RDMA from a contiguous host buffer.

Requirements:
  * libobstorcpp.so installed (or pointed at via OBSTORCPP_LIB).
  * Obstor server reachable on the configured endpoint with RDMA enabled.
"""

import os
from obstor import Obstor

client = Obstor(
    endpoint=os.environ.get("OBSTOR_ENDPOINT", "coe01:9000"),
    access_key=os.environ.get("OBSTOR_ACCESS_KEY", "obstoradmin"),
    secret_key=os.environ.get("OBSTOR_SECRET_KEY", "obstoradmin"),
    secure=False,
    enable_rdma=True,
)

if not client.bucket_exists(bucket_name="rdma-test"):
    client.make_bucket(bucket_name="rdma-test")

payload = bytearray(b"x" * (1 << 20))  # 1 MiB

resp = client.put_object(
    bucket_name="rdma-test",
    object_name="hello-rdma",
    data=payload,         # buffer-protocol object selects RDMA path
    length=len(payload),
)
print(f"etag={resp.etag} bucket={resp.bucket_name} object={resp.object_name}")
