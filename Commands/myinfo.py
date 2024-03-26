import time
import logging
from handler import MysqlUtils
from telegram import Update
from telegram.ext import ContextTypes

import bot
desc = '获取我的使用信息'
config = bot.config['bot']


def onQuery(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


def fmtTime(timestamp:float) -> str:
    tFormat = "%Y-%m-%d %H:%M:%S"
    return time.strftime(tFormat, time.localtime(timestamp))


def getContent(user:int,isPrivate:bool) -> str:
    flow = [
        '📋<b>个人信息</b>',
        '',
        '🎲<b>UID：</b>%s' % user[0],
        '📧<b>注册邮箱：</b>%s' % (user[8] if isPrivate else '***@***'),
        '⌚️<b>注册时间：</b>%s' % fmtTime(user[1]),
        '📚<b>套餐名称：</b>%s' % onQuery('SELECT name FROM v2_plan WHERE id = %s' % user[2])[0][0],
        '📌<b>到期时间：</b>%s' % ('长期有效' if user[3] is None else fmtTime(user[3])),
        '',
        '📤<b>上传流量：</b>%s GB' % round(user[4] / 1024 / 1024 / 1024, 2),
        '📥<b>下载流量：</b>%s GB' % round(user[5] / 1024 / 1024 / 1024, 2),
        '📃<b>剩余流量：</b>%s GB' % round((user[6]-user[5]-user[4]) / 1024 / 1024 / 1024, 2),
        '📜<b>总计流量：</b>%s GB' % round(user[6] / 1024 / 1024 / 1024, 2),
        '📊<b>上次使用：</b>%s' % fmtTime(user[7])
    ]

    return '\n'.join(flow)


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    userId = msg.from_user.id
    chatId = msg.chat_id
    chatType = msg.chat.type

    if chatType == 'private' or chatId == config['group_id']:
        callback = await msg.reply_text("请稍等...")
        msgId = callback.message_id

        try: 
            user = onQuery(
                'SELECT id,created_at,plan_id,expired_at,u,d,transfer_enable,t,email FROM v2_user WHERE `telegram_id` = %s' % userId)
            if chatType != 'private':
                context.job_queue.run_once(
                    bot.autoDelete, config["delete_time"], data=msg.id, chat_id=chatId, name=str(msg.id))
                context.job_queue.run_once(
                    bot.autoDelete, config["delete_time"], data=callback.message_id, chat_id=chatId, name=str(callback.message_id))
            if len(user) == 0:
                await context.bot.edit_message_text('%s\n你还没有绑定过账号！' % bot.text["fail"],chatId,msgId)
                return
            else:
                if user[0][2] is None:
                    await context.bot.edit_message_text('%s\n你的账号没有购买过订阅！' % bot.text["fail"],chatId,msgId)
                    return
                else:
                    text = getContent(user[0],chatType == 'private')
                    await context.bot.edit_message_text(text,chatId,msgId)
                    return 
        except Exception as error:
            logging.warning(error)
            await context.bot.edit_message_text('%s\n查询出现异常，请稍后再试！' % bot.text["fail"],chatId,msgId)
            return 
            