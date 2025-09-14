#!/usr/bin/env sh
set -eu

aws --version
aws stepfunctions list-state-machines --region "${AWS_DEFAULT_REGION}"