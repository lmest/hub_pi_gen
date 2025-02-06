import logging
import logging.config
import sys

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})

logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    datefmt='%d-%b-%y %H:%M:%S'
)