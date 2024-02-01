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

adminConfig = Config.parse_obj(get_driver().config).admin

# Blacklist Function
async def isBlacklistEnabled() -> bool:
    return adminConfig.enabled

async def isBlacklistCanHandle(event: Event) -> bool:
    logger.debug(isinstance(event, MemberJoinRequestEvent))
    if not isinstance(event, MemberJoinRequestEvent):
        return False
    logger.debug(adminConfig.domain)
    if adminConfig.domain == "*":
        return True
    if not len(adminConfig.domain):
        return False
    if adminConfig.domain[0] == "-":
        return event.group_id not in map(int, adminConfig.domain[1:].split(","))
    logger.debug(adminConfig.domain.split(","))
    return event.group_id in map(int, adminConfig.domain.split(","))

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