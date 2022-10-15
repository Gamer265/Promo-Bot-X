from . import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon.utils import get_peer_id

try:
    bot.start(bot_token=BOT_TOKEN)
except Exception as erc:
    log.info(str(erc))

sched = AsyncIOScheduler(timezone="Asia/Kolkata")
FUTURE = []
n = [0]
_n = [0]


async def update_msg_for_delete(e):
    lst = dB.get("DELETE_MSG") or []
    if e.id not in lst:
        lst.append(e.id)
        dB.set("DELETE_MSG", lst)
        await asyncio.sleep(1800)
        try:
            await e.delete()
            print(e.id, "deleted")
        except BaseException:
            pass
        lst = dB.get("DELETE_MSG") or []
        if e.id in lst:
            lst.remove(e.id)
            dB.set("DELETE_MSG", lst)


# @bot.on(events.NewMessage(chats=[MAIN_CHANNEL]))
# async def deleting_post(event):
#     try:
#         await asyncio.sleep(3)  # delay so other func can append id in db
#         lst = dB.get("DELETE_MSG")
#         if lst and event.id in dB.get("DELETE_MSG"):
#             await asyncio.sleep(60)
#             lst.remove(event.id)
#             dB.set("DELETE_MSG", lst)
#             await event.delete()
#     except Exception as error:
#         log.error(str(error))


@bot.on(events.NewMessage(incoming=True, pattern="^/start"))
async def strt(event):
    if str(event.sender_id) not in OWNER:
        return
    btn = [
        [Button.inline("RESTART BOT", data="restart")],
        [
            Button.inline("Start Every X min Promo", data="startpromo"),
            Button.inline("Stop Every X min Promo", data="stoppromo"),
        ],
        [
            Button.inline("Start Keyword Promo", data="kstartpromo"),
            Button.inline("Stop Keyword Promo", data="mkstoppromo"),
        ],
    ]
    await event.reply("Choose Options", buttons=btn)


@bot.on(events.NewMessage(incoming=True, pattern="^/help"))
async def help(e):
    msg = """
• `/start` - __Most Features Are Here__
• `/addpromo` - __This Will add Promo Massage__
• `/interval <in minutes>` - __To set Interval of promo__
• `/setkeyword <word>` - __To set keyword to trigger promo sender.__ **Default is** - `Over`
• `/status` - __To See Which Function Is Running.__
"""
    await e.reply(msg)


@bot.on(events.NewMessage(incoming=True, pattern="^/addpromo"))
async def addchh(event):
    if str(event.sender_id) not in OWNER:
        return
    chs = []
    async with bot.conversation(event.sender_id, timeout=500) as cv:
        await cv.send_message(
            "`Now send me Messages one by one. After Sending All the Message do `/done` .If you want to Cancel the Process do `/cancel` .`"
        )
        while True:
            x = await cv.get_response()
            if x.text.startswith("/cancel"):
                return await x.reply("`Process Cancelled Successfully`")
            elif x.text.startswith("/done"):
                break
            fwd = await x.forward_to(STORAGE_CHANNEL)
            chs.append(fwd.id)
            await x.reply("`Successfully Added`")
    dB.set("PROMO_DATA", chs)
    await event.reply(f"`Succesfully Added {len(chs)} Messages In Promo List.`")


@bot.on(events.NewMessage(incoming=True, pattern="^/status"))
async def addchh(event):
    if str(event.sender_id) not in OWNER:
        return
    await event.reply(
        f'`In Every X Min - {"Running..." if dB.get("EVERY_MIN") else "Stopped"}\nKeyword Promo - {"Running..." if dB.get("KEYPROMO") else "Stopped"}`'
    )


@bot.on(events.NewMessage(incoming=True, pattern="^/interval"))
async def intt(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        inn = event.text.split()[1]
    except:
        return await event.reply("`Invalid Input`")
    dB.set("INTERVAL", int(inn))
    await event.reply("`Done.`")


@bot.on(events.NewMessage(incoming=True, pattern="^/setkeyword"))
async def sett(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        key = event.text.split(" ", maxsplit=1)[1]
    except:
        return await event.reply("`Invalid Input`")
    dB.set("SPECIAL_WORD", key)
    await event.reply("`Done.`")


async def on_new_post(e):
    x = MAIN_CHANNEL
    sp = dB.get("SPECIAL_WORD") or "over"
    th = await e.get_chat()
    id = get_peer_id(th)
    if id != x:
        return
    try:
        if sp.lower() in e.text.lower():
            promos = dB.get("PROMO_DATA") or []
            if len(promos) <= _n[0]:
                _n[0] = 0
            xn = promos[_n[0]]
            msg = await bot.get_messages(STORAGE_CHANNEL, ids=xn)
            sxx = await bot.send_message(MAIN_CHANNEL, msg)
            asyncio.ensure_future(update_msg_for_delete(sxx))
            _n[0] += 1
    except Exception as ex:
        log.error(str(ex))


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("startpromo")))
async def _(e):
    xnx = dB.get("PROMO_DATA") or []
    if not xnx:
        return await e.reply("First Add Promo Msg")
    if not FUTURE:
        await e.reply("Successfully Started msg poster.")
        inter = dB.get("INTERVAL") or 30
        future = AsyncIOScheduler()
        future.add_job(on_every_min, "interval", minutes=inter, id="every_x_job")
        FUTURE.append(future)
        dB.set("EVERY_MIN", True)
        future.start()
        job()
    else:
        await e.reply("Msg post funcn already runningF")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("stoppromo")))
async def _(e):
    if FUTURE:
        x = await e.reply("Trying to stop msg post func.")
        FUTURE[0].remove_job("every_x_job")
        FUTURE.clear()
        dB.delete("EVERY_MIN")
        stop_job()
        await x.edit("`Done.`")
    else:
        await e.reply("Post func is not running.")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("kstartpromo")))
async def _(e):
    xnx = dB.get("PROMO_DATA") or []
    if not xnx:
        return await e.reply("First Add Promo Msg")
    if not dB.get("KEYPROMO"):
        await e.reply("Successfully Started msg poster.")
        try:
            bot.add_event_handler(on_new_post, events.NewMessage())
        except:
            pass
        dB.set("KEYPROMO", True)
    else:
        await e.reply("Msg post funcn already runningF")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("mkstoppromo")))
async def _(e):
    if dB.get("KEYPROMO"):
        x = await e.reply("Trying to stop msg post func.")
        try:
            bot.remove_event_handler(on_new_post)
        except:
            pass
        dB.delete("KEYPROMO")
        await x.edit("`Done.`")
    else:
        await e.reply("Post func is not running.")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("restart")))
async def restart(event):
    x = await event.reply("`Restarting...`")
    dB.set("RESTART", [x.id, x.chat_id])
    os.execl(sys.executable, sys.executable, "-m", "bot")


async def on_every_min():
    try:
        promos = dB.get("PROMO_DATA") or []
        if len(promos) <= n[0]:
            n[0] = 0
        xn = promos[n[0]]
        msg = await bot.get_messages(STORAGE_CHANNEL, ids=xn)
        sxx = await bot.send_message(MAIN_CHANNEL, msg)
        asyncio.ensure_future(update_msg_for_delete(sxx))
        n[0] += 1
    except Exception as error:
        log.error(str(error))


async def onstart():
    try:
        xx = dB.get("RESTART")
        if xx:
            x = await bot.get_messages(xx[1], ids=xx[0])
            await x.edit("`Restarted`")
            dB.delete("RESTART")
    except BaseException:
        dB.delete("RESTART")


async def speed_start():
    if FUTURE and dB.get("EVERY_MIN"):
        FUTURE[0].remove_job("every_x_job")
        FUTURE.clear()
        _inter = SPEED
        _future = AsyncIOScheduler()
        _future.add_job(on_every_min, "interval", minutes=_inter, id="severy_x_job")
        FUTURE.append(_future)
        _future.start()


async def stop_speed_start():
    if FUTURE and dB.get("EVERY_MIN"):
        FUTURE[0].remove_job("severy_x_job")
        FUTURE.clear()
        _inter = dB.get("INTERVAL") or 30
        _future = AsyncIOScheduler()
        _future.add_job(on_every_min, "interval", minutes=_inter, id="every_x_job")
        FUTURE.append(_future)
        _future.start()


def job():
    if FUTURE and dB.get("EVERY_MIN"):
        sched.add_job(speed_start, "cron", hour=SPEED_START_TIME)  # start time
        sched.add_job(stop_speed_start, "cron", hour=SPEED_STOP_TIME)  # stop time
        sched.start()


def stop_job():
    sched.shutdown(wait=False)


if dB.get("KEYPROMO"):
    bot.add_event_handler(on_new_post, events.NewMessage())

if dB.get("EVERY_MIN"):
    if not FUTURE:
        _inter = dB.get("INTERVAL") or 30
        _future = AsyncIOScheduler()
        _future.add_job(on_every_min, "interval", minutes=_inter, id="every_x_job")
        FUTURE.append(_future)
        _future.start()
    job()


log.info("Initialising Deletation....")


log.info("Started bot")
bot.loop.run_until_complete(onstart())
bot.run_until_disconnected()
