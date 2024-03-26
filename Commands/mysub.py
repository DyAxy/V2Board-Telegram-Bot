import time
import logging
from handler import MysqlUtils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import bot
desc = '获取我的订阅链接'
config = bot.config['bot']


def onQuery(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.sql_query(sql)
    finally:
        db.close()
        return result
    

def getContent(token: str) -> str:
    flow = [
        '📚<b>订阅链接</b>',
        '',
        '🔮通用订阅地址为（点击即可复制）：',
        '<code>%s/api/v1/client/subscribe?token=%s</code>' % (config['sublink'], token),
        '',
        '⚠️<b>如果订阅链接泄露请前往官网重置！</b>'
    ]
    keyboard = [InlineKeyboardButton("点我去官网", url=config['website'])]
    reply_markup = InlineKeyboardMarkup([keyboard])

    return '\n'.join(flow),reply_markup


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    userId = msg.from_user.id
    chatId = msg.chat_id
    chatType = msg.chat.type

    if chatType == 'private':
        callback = await msg.reply_text("请稍等...")
        msgId = callback.message_id
        try:
            user = onQuery('SELECT token FROM v2_user WHERE `telegram_id` = %s' % userId)
            if len(user) == 0:
                await context.bot.edit_message_text('%s\n你还没有绑定过账号！' % bot.text["fail"],chatId,msgId)
                return
            else:
                text, reply_markup = getContent(user[0][0])
                await context.bot.edit_message_text(text,chatId,msgId, reply_markup=reply_markup)
                return
        except Exception as error:
            logging.warning(error)
            await context.bot.edit_message_text('%s\n查询出现异常，请稍后再试！' % bot.text["fail"],chatId,msgId)
            return
    else:
        if chatId == config["group_id"]:
            callback = await msg.reply_text('%s\n为了你的账号安全，请私聊我！' % bot.text["fail"])
            context.job_queue.run_once(
                bot.autoDelete, config["delete_time"], data=msg.id, chat_id=chatId, name=str(msg.id))
            context.job_queue.run_once(
                bot.autoDelete, config["delete_time"], data=callback.message_id, chat_id=chatId, name=str(callback.message_id))
            return