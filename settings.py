from enum import Enum

from loguru import logger

LOGGER = logger
LOGGER.add(
    "logs/logs.log",
    rotation="10 KB",
    format="{time} {level} {message}",
    level="ERROR"
)


class Month(Enum):
    Jan = 1
    Feb = 2
    Mar = 3
    Apr = 4
    May = 5
    Jun = 6
    Jul = 7
    Aug = 8
    Sep = 9
    Oct = 10
    Nov = 11
    Dec = 12
