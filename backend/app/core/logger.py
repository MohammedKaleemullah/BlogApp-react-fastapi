import logging
import sys
import json_log_formatter

formatter = json_log_formatter.JSONFormatter()

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger("blog_app_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

