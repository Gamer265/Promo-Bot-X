import asyncio
import logging
import random
import os
import sys
import re

from telethon import TelegramClient, events, Button
from redis import Redis
from localdb import Database
from ._database import RedisDb
from .config import *

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
)
log = logging.getLogger(__name__)


try:
    bot = TelegramClient(
        None, api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e"
    )
except Exception as ex:
    log.error(ex)
    exit(0)


try:
    if REDISHOST:
        _redis_client = Redis(
            host=REDISHOST,
            password=REDISPASSWORD,
            port=REDISPORT,
            charset="utf-8",
            decode_responses=True,
        )
        dB = RedisDb(_redis_client)
        log.info("using redis db")
    else:
        dB = Database()
        log.info("using local db")
except Exception as dber:
    log.error(str(dber))
    exit(0)
