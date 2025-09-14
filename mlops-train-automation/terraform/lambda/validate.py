import json
import os
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)




def handler(event, context):
    """Dummy validation step.
    Expects JSON input with optional keys like {"source": "gitlab-ci", "commit": "abc123"}.
    Returns a validation result that the Step Function will pass to the next step.
    """
    logger.info("Validating data...")
    logger.info("Incoming event: %s", json.dumps(event))


    # Example: pretend to validate some input payload
    validated = True
    issues = []


    result = {
        "validated": validated,
        "issues": issues,
        "commit": event.get("commit"),
        "source": event.get("source", "manual"),
        "env": {
            "AWS_REGION": os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"),
        },
    "message": "Validation completed"
    }


    logger.info("Validation result: %s", json.dumps(result))
    return result
