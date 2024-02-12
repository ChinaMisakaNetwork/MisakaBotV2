from .Config import Config
from Database import dbSession
from .Model import Blacklist

from nonebot import on_request, on_notice
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupRequestEvent, GroupIncreaseNoticeEvent
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

adminConfig.save("Configs/AutoAdmin.json")

# Blacklist Function
async def isBlacklistEnabled() -> bool:
    return adminConfig.enabled


async def isBlacklistReject() -> bool:
    return adminConfig.reject


async def isBlacklistCanHandle(event: Event) -> bool:
    if not isinstance(event, GroupRequestEvent):
        return False
    if not event.sub_type == "add":
        return False
    return (event.group_id in adminConfig.domain) or (
                "*" in adminConfig.domain and -event.group_id not in adminConfig.domain)


isBlacklistHandle = Rule(isBlacklistEnabled, isBlacklistReject, isBlacklistCanHandle)
blacklistResponser = on_request(rule=isBlacklistHandle, priority=adminConfig.priority, block=False)


@blacklistResponser.handle()
async def blacklistHandleFunction(matcher: Matcher, event: GroupRequestEvent, bot: Bot):
    session = dbSession()
    result = session.query(Blacklist).filter(Blacklist.id == event.user_id).first()
    session.close()
    if result is not None:
        await event.reject(bot=bot, reason=adminConfig.blacklist_message)
        matcher.stop_propagation()

async def isBlacklistKick() -> bool:
    return adminConfig.kick


async def isBlacklistCanKickWhenNewMember(event: GroupIncreaseNoticeEvent) -> bool:
    return (event.group_id in adminConfig.domain) or ("*" in adminConfig.domain and -event.group_id not in adminConfig.domain)

isBlacklistKickNewMember = Rule(isBlacklistEnabled, isBlacklistKick, isBlacklistCanKickWhenNewMember)
blacklistKickOnNewMemberResponser = on_notice(rule=isBlacklistKickNewMember, priority=adminConfig.priority, block=False)

@blacklistKickOnNewMemberResponser.handle()
async def blacklistKickNewMemberFunction(matcher: Matcher, event: GroupIncreaseNoticeEvent, bot: Bot):
    session = dbSession()
    result = session.query(Blacklist).filter(Blacklist.id == event.user_id).first()
    session.close()
    if result is not None:
        await bot.set_group_kick(group_id=event.group_id, user_id=event.user_id, reject_add_request=False)
        matcher.stop_propagation()

