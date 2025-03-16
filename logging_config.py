# logging_config.py
import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,  # Set the default log level
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
