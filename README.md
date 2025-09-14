# MLOps Train Automation (Terraform + Step Functions + Lambda + GitLab CI)

This repo provisions a two-step training pipeline on AWS and triggers it from GitLab CI.

## Prerequisites
- Terraform >= 1.5
- AWS account & IAM permissions to create: IAM roles/policies, Lambda, Step Functions
- AWS CLI configured locally (for manual tests)
- GitLab project with CI minutes

## 1) Build Lambda archives
```bash
cd terraform/lambda
zip -r validate.zip validate.py
zip -r log_metrics.zip log_metrics.py
````

> Rebuild the zips whenever you change the code.

## 2) Deploy infrastructure with Terraform

```bash
cd terraform
terraform init
terraform apply \
  -var="project_name=mlops-train-automation" \
  -var="aws_region=eu-central-1"
```

Terraform output will include the **state\_machine\_arn**. Copy it for later (also visible in AWS Console).

## 3) Manual test of the Step Function

* **Console**: AWS Console → Step Functions → your state machine → *Start execution* → paste JSON input (see below) → Start.
* **CLI**:

```bash
aws stepfunctions start-execution \
  --state-machine-arn <YOUR_SFN_ARN> \
  --name "manual-$(date +%s)" \
  --input '{"source":"manual","commit":"local-test"}'
```

### Example JSON input

```json
{
  "source": "gitlab-ci",
  "commit": "abc123"
}
```

## 4) GitLab CI

This pipeline uses the official AWS CLI image and starts the Step Function on each push.

### Variables to set in GitLab → Settings → CI/CD → Variables

* `SFN_ARN` – ARN of the Step Functions state machine (Terraform output)
* `AWS_DEFAULT_REGION` – e.g. `eu-central-1`

**Auth option A (Access Keys):**

* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`

**Auth option B (OIDC, recommended):**

* `AWS_ROLE_ARN` – an IAM role in your AWS account trusted for your GitLab OIDC provider
* Enable CI Job Token (`CI_JOB_JWT`) in GitLab (default on)

On push, GitLab will run `train-model` and call `aws stepfunctions start-execution` with a JSON payload containing the commit SHA.

## Architecture

* **Lambda: validate → log\_metrics**
* **Step Functions** orchestrates sequential tasks
* **Terraform** fully describes IAM, Lambda, and the state machine
* **GitLab CI** triggers the pipeline per push with input parameters

## Clean up

```bash
cd terraform
terraform destroy
```

## Notes

* You can extend the pipeline by adding more Lambda tasks (e.g., `prepare_data`, `train_model`, `register_model`) and chaining them in the state machine definition.

```
```
