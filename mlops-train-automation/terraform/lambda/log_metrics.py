import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Dummy metrics logging step.
    Consumes the output of the Validate step and 'logs' metrics.
    """
    logger.info("Logging metrics...")
    logger.info("Incoming event: %s", json.dumps(event))

    # Fake metrics
    metrics = {
        "samples": 1234,
        "features": 42,
        "accuracy": 0.91,
        "loss": 0.37,
    }

    result = {
        "logged": True,
        "metrics": metrics,
        "message": "Metrics logged"
    }

    logger.info("Metrics result: %s", json.dumps(result))
    return result
