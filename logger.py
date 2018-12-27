import logging

# set basic logger information
logging.basicConfig(
    format="%(asctime)s - %(threadName)s: %(message)s", level=logging.INFO
)

# expose logger instance
EdwardLogger = logging.getLogger()
