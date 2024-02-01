from .Config import Config
from Database import dbSession
from .Model import Blacklist

from nonebot import on_request, get_driver
from nonebot.adapters import Event
from nonebot.adapters.mirai2.bot import Bot
from nonebot.adapters.mirai2.event.request import MemberJoinRequestEvent
from nonebot.rule import Rule
from nonebot.matcher import Matcher

from nonebot import logger
import os, json

def createConfig():
    configText = Config().dumps()
    with open("Configs/AutoAdmin.json", "w") as file:
        file.write(configText)
        file.flush()


if not os.path.exists("Configs/AutoAdmin.json"):
    createConfig()
    logger.info("Config created.")

try:
    adminConfig = Config.parse_obj(json.load(open("Configs/AutoAdmin.json")))
except json.JSONDecodeError:
    logger.warning("Corrupted config, plugin disabled")
    adminConfig = Config()
    adminConfig.enabled = False

# Blacklist Function
async def isBlacklistEnabled() -> bool:
    return adminConfig.enabled

async def isBlacklistCanHandle(event: Event) -> bool:
    if not isinstance(event, MemberJoinRequestEvent):
        return False
    return (event.group_id in adminConfig.domain) or ("*" in adminConfig.domain and -event.group_id not in adminConfig.domain)

isBlacklistHandle = Rule(isBlacklistEnabled, isBlacklistCanHandle)

blacklistResponser = on_request(rule=isBlacklistHandle, priority=adminConfig.priority, block=False)
@blacklistResponser.handle()
async def blacklistHandleFunction(matcher: Matcher, event: Event, bot: Bot):
    session = dbSession()
    result = session.query(Blacklist).filter(Blacklist.id == event.from_id).first()
    session.close()
    if result is not None:
        await event.reject(operate=1, bot=bot, message=adminConfig.blacklist_message)
        matcher.stop_propagation()