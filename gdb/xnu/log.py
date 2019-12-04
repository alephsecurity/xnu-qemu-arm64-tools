import logging

def setup_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if len(logger.handlers) == 0:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
