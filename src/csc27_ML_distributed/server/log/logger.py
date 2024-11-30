import sys
from logging import INFO, StreamHandler, getLogger

logger = getLogger("server")
logger.addHandler(StreamHandler(sys.stdout))
logger.setLevel(INFO)
