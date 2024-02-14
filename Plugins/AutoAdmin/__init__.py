from .Config import Config
from Database import dbSession
from .Model import Blacklist, AdminUser

from nonebot import on_request, on_notice, CommandGroup
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import (
    GroupRequestEvent,
    GroupIncreaseNoticeEvent,
    MessageEvent,
    GroupMessageEvent
)
from nonebot.rule import Rule, is_type
from nonebot.matcher import Matcher

from typing import Annotated
from nonebot.params import ShellCommandArgv

from nonebot import logger
import os, json
import asyncio, time
from datetime import timedelta

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


async def isBlacklistCanHandle(event: GroupRequestEvent) -> bool:
    if not event.sub_type == "add":
        return False
    return (event.group_id in adminConfig.domain) or (
        "*" in adminConfig.domain and -event.group_id not in adminConfig.domain
    )


isBlacklistHandle = Rule(
    isBlacklistEnabled, isBlacklistReject, isBlacklistCanHandle
) & is_type(GroupRequestEvent)
blacklistResponser = on_request(
    rule=isBlacklistHandle, priority=adminConfig.priority, block=False
)


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
    return (event.group_id in adminConfig.domain) or (
        "*" in adminConfig.domain and -event.group_id not in adminConfig.domain
    )


isBlacklistKickNewMember = Rule(
    isBlacklistEnabled, isBlacklistKick, isBlacklistCanKickWhenNewMember
) & is_type(GroupIncreaseNoticeEvent)
blacklistKickOnNewMemberResponser = on_notice(
    rule=isBlacklistKickNewMember, priority=adminConfig.priority, block=False
)


@blacklistKickOnNewMemberResponser.handle()
async def blacklistKickNewMemberFunction(
    matcher: Matcher, event: GroupIncreaseNoticeEvent, bot: Bot
):
    session = dbSession()
    result = session.query(Blacklist).filter(Blacklist.id == event.user_id).first()
    session.close()
    if result is not None:
        await bot.set_group_kick(
            group_id=event.group_id, user_id=event.user_id, reject_add_request=False
        )
        matcher.stop_propagation()


async def adminHandle(event: MessageEvent) -> bool:
    if event.message_type == "group":
        return (event.group_id in adminConfig.domain) or (
            "*" in adminConfig.domain and -event.group_id not in adminConfig.domain
        )
    return True


adminCommandRule = Rule(isBlacklistEnabled, adminHandle) & is_type(MessageEvent)
adminGroup = CommandGroup("admin", rule=adminCommandRule)

pardonHandler = adminGroup.shell_command("pardon")


@pardonHandler.handle()
async def pardonHandleFunction(
    event: MessageEvent,
    bot: Bot,
    message: Annotated[list[str | MessageSegment], ShellCommandArgv()],
):
    session = dbSession()
    adminQuery = session.query(AdminUser).filter(AdminUser.id == event.user_id).first()
    if adminQuery is None:
        session.close()
        return
    if adminQuery.tier <= 0:
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 权限不足，请向更高阶的风纪委员询问"),
            at_sender=True,
            reply_message=True,
        )
        session.close()
        return
    if len(message) != 1:
        await bot.send(
            event=event,
            message=Message(
                f"[CQ:at,qq={event.user_id}] 参数数量不正确。pardon拥有1个参数，但提供了{len(message)}个。"
            ),
            at_sender=True,
            reply_message=True,
        )
        session.close()
        return
    try:
        pid = int(message[0])
        assert pid > 0
    except:
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 参数类型不正确。参数1需为正整数。"),
            at_sender=True,
            reply_message=True,
        )
        session.close()
        return
    blackQuery = session.query(Blacklist).filter(Blacklist.id == pid).first()
    if blackQuery:
        session.delete(blackQuery)
        session.commit()
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 删除成功。"),
            at_sender=True,
            reply_message=True,
        )
    else:
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 账号{pid}不存在于黑名单中。"),
            at_sender=True,
            reply_message=True,
        )
    session.close()


pardonHandler = adminGroup.shell_command("ban")


@pardonHandler.handle()
async def pardonBanFunction(
    event: MessageEvent,
    bot: Bot,
    message: Annotated[list[str | MessageSegment], ShellCommandArgv()],
):
    session = dbSession()
    adminQuery = session.query(AdminUser).filter(AdminUser.id == event.user_id).first()
    if adminQuery is None:
        session.close()
        return
    if adminQuery.tier <= 0:
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 权限不足，请向更高阶的风纪委员询问"),
            at_sender=True,
            reply_message=True,
        )
        session.close()
        return
    if len(message) != 1:
        await bot.send(
            event=event,
            message=Message(
                f"[CQ:at,qq={event.user_id}] 参数数量不正确。pardon拥有1个参数，但提供了{len(message)}个。"
            ),
            at_sender=True,
            reply_message=True,
        )
        session.close()
        return
    try:
        pid = int(message[0])
        assert pid > 0
    except:
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 参数类型不正确。参数1需为正整数。"),
            at_sender=True,
            reply_message=True,
        )
        session.close()
        return
    blackQuery = session.query(Blacklist).filter(Blacklist.id == pid).first()
    if blackQuery:
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 账号{pid}已经存在于黑名单中。"),
            at_sender=True,
            reply_message=True,
        )
    else:
        blackObject = Blacklist(pid)
        session.add(blackObject)
        session.commit()
        if "*" in adminConfig.domain:
            adminList = [j["group_d"] for j in await bot.get_group_list()]
            for item in adminConfig.domain:
                if isinstance(item, int):
                    adminList.remove(-item)
        else:
            adminList = adminConfig.domain
        count = 0
        for group in adminList:
            groupMemberList = await bot.get_group_member_list(group_id=group)
            if pid in [i["user_id"] for i in groupMemberList]:
                await bot.set_group_kick(
                    group_id=group, user_id=pid, reject_add_request=False
                )
                count += 1
        if count:
            messageSend = f"[CQ:at,qq={event.user_id}] 已添加, 并于{count}个群内移除该用户。"
        else:
            messageSend = f"[CQ:at,qq={event.user_id}] 已添加。"
        messageSend = Message(messageSend)
        await bot.send(
            event=event, message=messageSend, at_sender=True, reply_message=True
        )

    session.close()

class MuteCoroutine:
    operated = False
    def __init__(self, owner, group):
        self.users = []
        self.owner = owner
        self.group = group
        self.time = time.time()
        self.users.append(owner)

ongoingMute = {}

async def muteBroadcast(event, bot):
    if event.group_id in ongoingMute:
        await bot.send_group_msg(
            group_id=event.group_id,
            message=Message(f"全体禁言排程进行中 ({len(ongoingMute[event.group_id].users)}/{adminConfig.mute_approve})\n排程将于{str(timedelta(seconds=int(adminConfig.mute_cancel_after - (time.time()-ongoingMute[event.group_id].time))))}后失效。"),
        )

muteHandler = adminGroup.shell_command("mute", rule=is_type(GroupMessageEvent))
@muteHandler.handle()
async def muteHandleFunction(
    event: GroupMessageEvent,
    bot: Bot,
    message: Annotated[list[str | MessageSegment], ShellCommandArgv()]
):
    session = dbSession()
    adminQuery = session.query(AdminUser).filter(AdminUser.id == event.user_id).first()
    session.close()
    if adminQuery is None:
        return
    if adminQuery.tier <= 0:
        await bot.send(
            event=event,
            message=Message(f"[CQ:at,qq={event.user_id}] 权限不足，请向更高阶的风纪委员询问"),
            at_sender=True,
            reply_message=True,
        )
        return
    if len(message) > 2:
        await bot.send(
            event=event,
            message=Message(
                f"[CQ:at,qq={event.user_id}] 参数数量不正确。mute拥有最多1个参数，但提供了{len(message)}个。"
            ),
            at_sender=True,
            reply_message=True,
        )
        return
    force = False
    if len(message):
        if message[0].lower() not in ["true", "false", "cancel"]:
            await bot.send(
                event=event,
                message=Message(
                    f"[CQ:at,qq={event.user_id}] 参数类型不正确。参数1需为布尔值(true, false)或者cancel。"
                ),
                at_sender=True,
                reply_message=True,
            )
            return
        force = (message[0].lower() == "true")
        if message[0].lower() == "cancel":
            if event.group_id not in ongoingMute or ongoingMute[event.group_id].operated:
                await bot.send(
                    event=event,
                    message=Message(
                        f"[CQ:at,qq={event.user_id}] 此群没有排定的全体禁言请求。"
                    ),
                    at_sender=True,
                    reply_message=True,
                )
                return
            if ongoingMute[event.group_id].owner == event.user_id or adminQuery.tier >= adminConfig.mute_super_priv:
                ongoingMute[event.group_id].operated=True
                del ongoingMute[event.group_id]
                await bot.send(
                    event=event,
                    message=Message(
                        f"[CQ:at,qq={event.user_id}] 已取消。"
                    ),
                    at_sender=True,
                    reply_message=True
                )
                return
    if force:
        if adminQuery.tier < adminConfig.mute_super_priv:
            await bot.send(
                event=event,
                message=Message(f"[CQ:at,qq={event.user_id}] 权限不足，已经自动更改为排定全体禁言请求。"),
                at_sender=True,
                reply_message=True,
            )
        else:
            await bot.set_group_whole_ban(group_id = event.group_id, enable=True)
            await bot.send(
                event=event,
                message=Message(f"[CQ:at,qq={event.user_id}] 已经强制开启全体禁言。"),
                at_sender=True,
                reply_message=True,
            )
            if event.group_id in ongoingMute:
                ongoingMute[event.group_id].operated = True
                del ongoingMute[event.group_id]
            return

    if event.group_id in ongoingMute:
        object = ongoingMute[event.group_id]
        if event.user_id in object.users:
            await bot.send(
                event=event,
                message=Message(f"[CQ:at,qq={event.user_id}] 你已经对此群的全体禁言做出表态了。"),
                at_sender=True,
                reply_message=True,
            )
        else:
            object.users.append(event.user_id)
            await bot.send(
                event=event,
                message=Message(f"[CQ:at,qq={event.user_id}] 表态成功。"),
                at_sender=True,
                reply_message=True,
            )
            if len(object.users) >= adminConfig.mute_approve:
                await bot.set_group_whole_ban(group_id=event.group_id, enable=True)
                await bot.send_group_message(group_id=event.group_id, message="全体禁言已通过。")
                object.operated = True
                if event.group_id in ongoingMute:
                    del ongoingMute[event.group_id]
            else:
                await muteBroadcast(event, bot)
        return
    ongoingMute[event.group_id] = MuteCoroutine(event.user_id, event.group_id)

    loop = asyncio.get_running_loop()
    def generateTask(taskObject, bot):
        async def Task():
            await asyncio.sleep(adminConfig.mute_cancel_after)
            if not taskObject.operated:
                taskObject.operated = False
                del ongoingMute[taskObject.group]
                await bot.send_group_msg(group_id=taskObject.group, message="全体禁言申请未通过。")
        return Task()

    asyncio.ensure_future(generateTask(ongoingMute[event.group_id], bot), loop=loop)
    await muteBroadcast(event, bot)