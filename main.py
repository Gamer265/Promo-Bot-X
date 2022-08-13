import subprocess, sys, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config

process = []
START_TIME = config("START_TIME", default="6:0")
STOP_TIME = config("STOP_TIME", default="1:30")

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
    sched.add_job(kill, "cron", hour=STOP_TIME.split(":")[0], minute=STOP_TIME.split(":")[1])  # stop time
    sched.start()

loop = asyncio.get_event_loop()

if START_TIME and STOP_TIME:
    loop.run_until_complete(job())
    

start()

loop.run_forever()
