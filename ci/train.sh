set -euo pipefail
set -x

aws --version
aws stepfunctions start-execution \
  --region "${AWS_DEFAULT_REGION}" \
  --state-machine-arn "${SFN_ARN}" \
  --name "train-$(date +%s)" \
  --input "{\"source\":\"gitlab-ci\",\"commit\":\"${CI_COMMIT_SHORT_SHA}\"}"