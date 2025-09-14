#!/bin/sh
set -eu

# Діагностика оточення (не друкує секрети)
aws --version
aws configure list
aws sts get-caller-identity

# Пуск Step Functions
aws stepfunctions start-execution \
  --region "${AWS_DEFAULT_REGION}" \
  --state-machine-arn "${SFN_ARN}" \
  --name "train-$(date +%s)" \
  --input "{\"source\":\"gitlab-ci\",\"commit\":\"${CI_COMMIT_SHORT_SHA}\"}"