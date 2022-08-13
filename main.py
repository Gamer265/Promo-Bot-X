import subprocess, sys, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config

process = []
START_TIME = config("START_TIME", default=None)
STOP_TIME = config("STOP_TIME", default=None)

def start():
    kill()
    p = subprocess.Popen(
        [sys.executable, "-m", "bot"],
        stdin=None,
        stderr=None,
        stdout=True,
        cwd=None,
    )
    process.append(p)


def kill():
    if process:
        process[0].terminate()
        process.clear()

async def job():
    sched = AsyncIOScheduler(timezone="Asia/Kolkata")
    sched.add_job(start, "cron", hour=START_TIME.split(":")[0], minute=START_TIME.split(":")[1])  # start time
    sched.add_job(kill, "cron", hour=STOP_TIME.split(":")[0], minute=STOO_TIME.split(":")[1])  # stop time
    sched.start()

if START_TIME and STOP_TIME:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(job())
    loop.run_forever()
else:
    start()
