terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name = var.project_name
}

# ---------------------------
# IAM for Lambda
# ---------------------------
resource "aws_iam_role" "lambda_exec" {
  name               = "${local.name}-lambda-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action   = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ---------------------------
# Lambda functions (built zips on disk)
# ---------------------------
resource "aws_lambda_function" "validate" {
  function_name = "${local.name}-validate"
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "python3.11"
  handler       = "validate.handler"
  filename      = "${path.module}/lambda/validate.zip"

  # Re-deploy when zip changes
  source_code_hash = filebase64sha256("${path.module}/lambda/validate.zip")
}

resource "aws_lambda_function" "log_metrics" {
  function_name = "${local.name}-log-metrics"
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "python3.11"
  handler       = "log_metrics.handler"
  filename      = "${path.module}/lambda/log_metrics.zip"

  source_code_hash = filebase64sha256("${path.module}/lambda/log_metrics.zip")
}

# ---------------------------
# IAM for Step Functions
# ---------------------------
resource "aws_iam_role" "sfn_role" {
  name               = "${local.name}-sfn-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "states.${var.aws_region}.amazonaws.com" }
      Action   = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "sfn_invoke_lambda" {
  name = "${local.name}-sfn-invoke-lambda"
  role = aws_iam_role.sfn_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction",
          "lambda:InvokeAsync"
        ],
        Resource = [
          aws_lambda_function.validate.arn,
          aws_lambda_function.log_metrics.arn
        ]
      }
    ]
  })
}

# ---------------------------
# Step Function (ValidateData -> LogMetrics)
# ---------------------------
resource "aws_sfn_state_machine" "train_pipeline" {
  name     = "${local.name}-state-machine"
  role_arn = aws_iam_role.sfn_role.arn

  definition = jsonencode({
    Comment = "Training pipeline: Validate -> LogMetrics",
    StartAt = "ValidateData",
    States = {
      ValidateData = {
        Type       = "Task",
        Resource   = aws_lambda_function.validate.arn,
        ResultPath = "$.validateResult",
        Next       = "LogMetrics"
      },
      LogMetrics = {
        Type       = "Task",
        Resource   = aws_lambda_function.log_metrics.arn,
        ResultPath = "$.logResult",
        End        = true
      }
    }
  })
}

output "state_machine_arn" {
  description = "ARN of the Step Functions state machine"
  value       = aws_sfn_state_machine.train_pipeline.arn
}
