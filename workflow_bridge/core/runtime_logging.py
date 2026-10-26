"""Standard logging only; no chat, model or pet runtime is loaded."""
import logging


def get_logger(name):
    logger = logging.getLogger("workflow_bridge." + name)
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger
