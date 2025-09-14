#!/usr/bin/env bash
set -euo pipefail
aws stepfunctions start-execution --region "${AWS_DEFAULT_REGION}" --state-machine-arn "${SFN_ARN}" --name "train-$(date +%s)" --input "{\"source\":\"gitlab-ci\",\"commit\":\"${CI_COMMIT_SHORT_SHA}\"}"
