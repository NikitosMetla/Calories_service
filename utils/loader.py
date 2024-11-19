import datetime
from loguru import logger

logger.add(f"logs/{datetime.date.today()}.log", format="{time:DD-MMM-YYYY HH:mm:ss} | {level:^25} | {message}",
           enqueue=True, rotation="00:00")

logger.level("JOIN", no=60, color="<green>")

logger.level("SPAM", no=60, color="<red>")
