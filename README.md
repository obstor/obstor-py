# Obstor Python Client SDK for Amazon S3 Compatible Cloud Storage [![Apache V2 License](https://img.shields.io/badge/license-Apache%20V2-blue.svg)](https://github.com/obstor/obstor-py/blob/master/LICENSE)

The Obstor Python Client SDK provides high level APIs to access any Obstor Object Storage or other Amazon S3 compatible service.

This Quickstart Guide covers how to install the Obstor client SDK, connect to the object storage service, and create a sample file uploader.

The example below uses:
- [Python version 3.10+](https://www.python.org/downloads/)
- The Obstor `demo` test server

The `demo` server is a public Obstor cluster located at [https://demo.obstor.net](https://demo.obstor.net).
This cluster runs the latest stable version of Obstor and may be used for testing and development.
The access credentials in the example are open to the public and all data uploaded to `demo` should be considered public and world-readable.

For a complete list of APIs and examples, see the [Python SDK Documentation](https://obstor.net/docs/enterprise/obstor-object-store/developers/sdk/python/)

## Install the Obstor Python SDK

The Python SDK requires Python version 3.10+.
You can install the SDK with `pip` or from the [`obstor/obstor-py` GitHub repository](https://github.com/obstor/obstor-py):

### Using `pip`

```sh
pip3 install obstor
```

### Using Source From GitHub

```sh
git clone https://github.com/obstor/obstor-py
cd obstor-py
python setup.py install
```

## Create a Obstor Client

To connect to the target service, create a Obstor client using the `Obstor()` method with the following required parameters:

| Parameter    | Description                                            |
|--------------|--------------------------------------------------------|
| `endpoint`   | URL of the target service.                             |
| `access_key` | Access key (user ID) of a user account in the service. |
| `secret_key` | Secret key (password) for the user account.            |

For example:

```py
from obstor import Obstor

client = Obstor(
    endpoint="demo.obstor.net",
    access_key="Q3AM3UQ867SPQQA43P2F",
    secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
)
```

## Example - File Uploader

This example does the following:

- Connects to the Obstor `demo` server using the provided credentials.
- Creates a bucket named `python-test-bucket` if it does not already exist.
- Uploads a file named `test-file.txt` from `/tmp`, renaming it `my-test-file.txt`.
- Verifies the file was created by listing the bucket with [`rclone`](https://rclone.org/s3/).

### `file_uploader.py`

```py
# file_uploader.py Obstor Python SDK example
from obstor import Obstor
from obstor.error import S3Error

def main():
    # Create a client with the Obstor server playground, its access key
    # and secret key.
    client = Obstor(
        endpoint="demo.obstor.net",
        access_key="Q3AM3UQ867SPQQA43P2F",
        secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    )

    # The file to upload, change this path if needed
    source_file = "/tmp/test-file.txt"

    # The destination bucket and filename on the Obstor server
    bucket_name = "python-test-bucket"
    destination_file = "my-test-file.txt"

    # Make the bucket if it doesn't exist.
    found = client.bucket_exists(bucket_name=bucket_name)
    if not found:
        client.make_bucket(bucket_name=bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name=bucket_name,
        object_name=destination_file,
        file_path=source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
```

To run this example:

1. Create a file in `/tmp` named `test-file.txt`.
   To use a different path or filename, modify the value of `source_file`.

2. Run `file_uploader.py` with the following command:

```sh
python file_uploader.py
```

If the bucket does not exist on the server, the output resembles the following:

```sh
Created bucket python-test-bucket
/tmp/test-file.txt successfully uploaded as object my-test-file.txt to bucket python-test-bucket
```

3. Verify the uploaded file with `rclone ls` (using an `obstor` remote configured for the `demo` server):

```sh
rclone ls obstor:python-test-bucket
    20480 my-test-file.txt
```

## RDMA / GPUDirect Storage (optional)

`put_object` and `get_object` can dispatch to Obstor's RDMA + GPUDirect
Storage path via [obstor-cpp](https://github.com/obstor/obstor-cpp). It is
strictly opt-in and the SDK stays pure-Python unless used.

```python
from obstor import Obstor

client = Obstor(
    endpoint="server:9000",
    access_key="...",
    secret_key="...",
    secure=False,
    enable_rdma=True,             # opt-in
)

buf = bytearray(1 << 20)
client.put_object(
    bucket_name="b", object_name="o",
    data=buf, length=len(buf),    # buffer-protocol object selects RDMA
)

dst = bytearray(1 << 20)
n = client.get_object(
    bucket_name="b", object_name="o",
    into=dst, length=len(dst),    # into= selects RDMA, returns bytes
)
```

Requires `libobstorcpp.so` (built with `-DOBSTOR_CPP_ENABLE_RDMA=ON`) on the
host's library search path (or pointed at via the `OBSTORCPP_LIB` env var).
GPU buffer pointers (e.g. CuPy's `arr.data.ptr`, PyTorch's `t.data_ptr()`)
work as `data=` / `into=` arguments unchanged — pass them as `int`.

See `examples/put_object_rdma.py` and `examples/get_object_rdma.py`.

## More References

* [Python SDK Documentation](https://obstor.net/docs/enterprise/obstor-object-store/developers/sdk/python/)
* [Examples](https://github.com/obstor/obstor-py/tree/master/examples)

## Explore Further

* [Complete Documentation](https://obstor.net/docs/enterprise/obstor-object-store/)

## Contribute

[Contributors Guide](https://github.com/obstor/obstor-py/blob/master/CONTRIBUTING.md)

## License

This SDK is distributed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0), see [LICENSE](https://github.com/obstor/obstor-py/blob/master/LICENSE) and [NOTICE](https://github.com/obstor/obstor-py/blob/master/NOTICE) for more information.

[![PYPI](https://img.shields.io/pypi/v/obstor.svg)](https://pypi.python.org/pypi/obstor)
