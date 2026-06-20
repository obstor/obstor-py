#!/usr/bin/env bash
#
# Obstor Python Library for Amazon S3 Compatible Cloud Storage, (C) 2020 MinIO, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

function run_obstor_server() {
	if [ ! -f tests/functional/obstor ]; then
		wget --quiet --output-document tests/functional/obstor https://dl.pgg.net/server/obstor/release/linux-amd64/obstor
		chmod +x tests/functional/obstor
	fi

	export OBSTOR_KMS_KES_ENDPOINT=https://demo.obstor.net:7373
	export OBSTOR_KMS_KES_KEY_FILE=tests/functional/demo.obstor.net.kes.root.key
	export OBSTOR_KMS_KES_CERT_FILE=tests/functional/demo.obstor.net.kes.root.cert
	export OBSTOR_KMS_KES_KEY_NAME=my-obstor-key
	export OBSTOR_NOTIFY_WEBHOOK_ENABLE_obstorpytest=on
	export OBSTOR_NOTIFY_WEBHOOK_ENDPOINT_obstorpytest=http://example.org/
	export SQS_ARN="arn:obstor:sqs::obstorpytest:webhook"
	export OBSTOR_CI_CD=1
	tests/functional/obstor server --config-dir tests/functional/.cfg tests/functional/.d{1...4} >tests/functional/obstor.log 2>&1 &
}

if [ -z ${SERVER_ENDPOINT+x} ]; then
	run_obstor_server
	OBSTOR_PID=$!
	trap 'kill -9 ${OBSTOR_PID} 2>/dev/null' INT

	export TESTS_MODE=full
	export SERVER_ENDPOINT=localhost:9000
	export ACCESS_KEY=obstoradmin
	export SECRET_KEY=obstoradmin
	export ENABLE_HTTPS=0
fi

PYTHONPATH=$PWD python tests/functional/tests.py
if [ -n "$OBSTOR_PID" ]; then
	kill -9 "$OBSTOR_PID" 2>/dev/null
fi
