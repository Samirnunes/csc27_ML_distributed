import sys
from logging import getLogger, StreamHandler, INFO

logger = getLogger("server")
logger.addHandler(StreamHandler(sys.stdout))
logger.setLevel(INFO)
