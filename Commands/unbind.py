import logging
from handler import MysqlUtils
from telegram import Update
from telegram.ext import ContextTypes

import bot
desc = '解绑该账号的 Telegram 账号'
config = bot.config['bot']


def onQuery(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    userId = msg.from_user.id
    chatId = msg.chat_id
    chatType = msg.chat.type
    if chatType == 'private':
        callback = await msg.reply_text("请稍等...")
        msgId = callback.message_id
        try:
            userResult = onQuery("SELECT id FROM v2_user WHERE `telegram_id` = %s" % userId)
            if len(userResult) == 0:
                await context.bot.edit_message_text('%s\n你还没有绑定过账号！' % bot.text["fail"],chatId,msgId)
                return
            else:
                db = MysqlUtils(port=bot.port)
                db.execute_sql('UPDATE v2_user SET telegram_id = NULL WHERE `telegram_id` = %s' % userId)
                db.conn.commit()
                db.close()
                await context.bot.edit_message_text('%s\n你已成功解绑 Telegram 了！' % bot.text["okay"],chatId,msgId)
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