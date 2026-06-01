import logging

from new_pipeline.core.logging import configure_logging


def test_logging_configures_logger(tmp_path):
    logger = configure_logging()
    assert isinstance(logger, logging.Logger)
