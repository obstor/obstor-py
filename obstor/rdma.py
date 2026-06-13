# -*- coding: utf-8 -*-
# Obstor Python Library for Amazon S3 Compatible Cloud Storage,
# (C) [2024] - [2026] MinIO, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# SPDX-License-Identifier: Apache-2.0

"""RDMA / GPUDirect Storage dispatch via libobstorcpp.so.

Loaded lazily on first use when ``Obstor(enable_rdma=True)`` was set.
``libobstorcpp.so`` must be findable via the platform loader
(``LD_LIBRARY_PATH`` on Linux, or the path in the ``OBSTORCPP_LIB`` env var).
"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
from typing import Optional, Union


class RDMANotAvailable(RuntimeError):
    """libobstorcpp.so could not be loaded."""


class RDMAError(RuntimeError):
    """libobstorcpp.so returned an error from a put/get call."""


_LIB: Optional[ctypes.CDLL] = None


def _load() -> ctypes.CDLL:
    """Load libobstorcpp.so once and register all ctypes signatures."""
    global _LIB  # pylint: disable=global-statement
    if _LIB is not None:
        return _LIB

    path = os.environ.get("OBSTORCPP_LIB")
    if not path:
        path = ctypes.util.find_library("obstorcpp") or "libobstorcpp.so"
    try:
        lib = ctypes.CDLL(path)
    except OSError as exc:
        raise RDMANotAvailable(
            f"failed to load libobstorcpp.so ({path}): {exc}. "
            "Install obstor-cpp with -DOBSTOR_CPP_ENABLE_RDMA=ON "
            "or set OBSTORCPP_LIB."
        ) from exc

    void_p = ctypes.c_void_p
    c_char_p = ctypes.c_char_p
    c_size_t = ctypes.c_size_t
    c_ssize_t = ctypes.c_ssize_t
    c_int = ctypes.c_int
    char_buf64 = ctypes.c_char * 64

    lib.obstorcpp_client_new.argtypes = [
        c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int,
    ]
    lib.obstorcpp_client_new.restype = void_p

    lib.obstorcpp_client_free.argtypes = [void_p]
    lib.obstorcpp_client_free.restype = None

    lib.obstorcpp_put_object.argtypes = [
        void_p, c_char_p, c_char_p, void_p, c_size_t,
        void_p, void_p, char_buf64, char_buf64,
    ]
    lib.obstorcpp_put_object.restype = c_ssize_t

    lib.obstorcpp_get_object.argtypes = [
        void_p, c_char_p, c_char_p, void_p, c_size_t, void_p, void_p,
    ]
    lib.obstorcpp_get_object.restype = c_ssize_t

    lib.obstorcpp_alloc_aligned.argtypes = [c_size_t]
    lib.obstorcpp_alloc_aligned.restype = void_p

    lib.obstorcpp_free_aligned.argtypes = [void_p]
    lib.obstorcpp_free_aligned.restype = None

    lib.obstorcpp_rdma_available.argtypes = []
    lib.obstorcpp_rdma_available.restype = c_int

    lib.obstorcpp_last_error.argtypes = []
    lib.obstorcpp_last_error.restype = c_char_p

    _LIB = lib
    return lib


def is_available() -> bool:
    """True if libobstorcpp.so loaded and cuObj is connected to cuObjServer."""
    try:
        return _load().obstorcpp_rdma_available() != 0
    except RDMANotAvailable:
        return False


def alloc_aligned(size: int) -> int:
    """Allocate a page-aligned buffer.

    Returns a raw pointer as int, or 0 on failure.
    """
    return _load().obstorcpp_alloc_aligned(size) or 0


def free_aligned(ptr: int) -> None:
    """Release a buffer previously returned by :func:`alloc_aligned`."""
    _load().obstorcpp_free_aligned(ptr)


def _last_error(lib: ctypes.CDLL) -> str:
    """Return the thread-local last error string from libobstorcpp."""
    msg = lib.obstorcpp_last_error()
    return msg.decode() if msg else "unknown error"


def _buffer_pointer(
    buf: Union[int, memoryview, bytes, bytearray],
) -> tuple[int, int]:
    """Return (ptr, length) for a buffer-protocol object or raw int pointer.

    For raw int pointers the caller-supplied length is unknown; returns 0
    for length and the caller must pass it separately.
    """
    if isinstance(buf, int):
        return buf, 0
    if isinstance(buf, (bytes, bytearray)):
        return ctypes.cast(
            (ctypes.c_char * len(buf)).from_buffer_copy(buf)
            if isinstance(buf, bytes)
            else (ctypes.c_char * len(buf)).from_buffer(buf),
            ctypes.c_void_p,
        ).value or 0, len(buf)
    if isinstance(buf, memoryview):
        if not buf.contiguous:
            raise ValueError("memoryview must be contiguous for RDMA")
        backing = buf if not buf.readonly else bytearray(buf)
        addr = ctypes.addressof(
            (ctypes.c_char * buf.nbytes).from_buffer(backing)
        )
        return addr, buf.nbytes
    raise TypeError(
        f"unsupported buffer type for RDMA: {type(buf).__name__}; "
        "pass memoryview, bytearray, bytes, or raw int pointer"
    )


class RDMAClient:
    """Wraps a single obstorcpp_client* handle."""

    # pylint: disable=too-many-positional-arguments,too-many-arguments
    def __init__(self, endpoint: str, region: str, access_key: str,
                 secret_key: str, session_token: str, secure: bool):
        lib = _load()
        self._lib = lib
        self._handle = lib.obstorcpp_client_new(
            endpoint.encode(),
            region.encode() if region else b"",
            access_key.encode() if access_key else b"",
            secret_key.encode() if secret_key else b"",
            session_token.encode() if session_token else b"",
            1 if secure else 0,
        )
        if not self._handle:
            raise RDMAError(f"obstorcpp_client_new: {_last_error(lib)}")

    def close(self) -> None:
        """Release the underlying obstorcpp_client* handle."""
        if self._handle:
            self._lib.obstorcpp_client_free(self._handle)
            self._handle = None

    def __del__(self):
        self.close()

    def put(self, bucket: str, obj: str,
            buf: Union[int, memoryview, bytes, bytearray],
            length: Optional[int] = None) -> tuple[int, str, str]:
        """Put ``buf`` to ``bucket/obj`` via RDMA.

        Returns (bytes, etag, checksum).
        """
        ptr, inferred = _buffer_pointer(buf)
        size = length if length is not None else inferred
        if size <= 0:
            raise ValueError("length must be > 0 for RDMA put")
        etag = (ctypes.c_char * 64)()
        checksum = (ctypes.c_char * 64)()
        nbytes = self._lib.obstorcpp_put_object(
            self._handle, bucket.encode(), obj.encode(),
            ctypes.c_void_p(ptr), size, None, None, etag, checksum,
        )
        if nbytes < 0:
            raise RDMAError(f"RDMA put: {_last_error(self._lib)}")
        return (
            int(nbytes),
            etag.value.decode().replace('"', ""),
            checksum.value.decode(),
        )

    def get(self, bucket: str, obj: str,
            buf: Union[int, memoryview, bytearray],
            length: Optional[int] = None) -> int:
        """RDMA-get ``bucket/obj`` into ``buf``; returns the byte count."""
        ptr, inferred = _buffer_pointer(buf)
        size = length if length is not None else inferred
        if size <= 0:
            raise ValueError("length must be > 0 for RDMA get")
        nbytes = self._lib.obstorcpp_get_object(
            self._handle, bucket.encode(), obj.encode(),
            ctypes.c_void_p(ptr), size, None, None,
        )
        if nbytes < 0:
            raise RDMAError(f"RDMA get: {_last_error(self._lib)}")
        return int(nbytes)
