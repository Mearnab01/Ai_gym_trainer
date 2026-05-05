import logging

def setup_logger():
    logger = logging.getLogger("AI_GYM")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)

        fh = logging.FileHandler("app.log")
        fh.setFormatter(formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger