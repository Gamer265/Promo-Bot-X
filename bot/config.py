from decouple import config
from dotenv import load_dotenv

load_dotenv()


try:
    BOT_TOKEN = config("BOT_TOKEN")
    OWNER = config("OWNER")
    STORAGE_CHANNEL = config("STORAGE_CHANNEL", cast=int)
    MAIN_CHANNEL = config("MAIN_CHANNEL", cast=int)
    

    # for railway

    REDISPASSWORD = config("REDISPASSWORD", default=None)
    REDISHOST = config("REDISHOST", default=None)
    REDISPORT = config("REDISPORT", default=None)
    REDISUSER = config("REDISUSER", default=None)
except Exception as ex:
    print(ex)
    exit(0)
