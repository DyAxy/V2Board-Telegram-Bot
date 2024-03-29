import logging
from handler import MysqlUtils
from telegram import Update
from telegram.ext import ContextTypes

import bot
desc = "绑定账号信息到该 Telegram 账号"
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
            # 指令参数长度不为 1
            if len(context.args) != 1:
                await context.bot.edit_message_text('%s\n绑定请输入： /bind 订阅地址' % bot.text["fail"],chatId,msgId)
                return
            # 订阅链接分割不为 2
            subInfo = context.args[0].split('=')
            if len(subInfo) != 2:
                await context.bot.edit_message_text('%s\n绑定请输入： /bind 订阅地址' % bot.text["fail"],chatId,msgId)
                return
            # 判断该 userId 是否在库
            userResult = onQuery("SELECT id FROM v2_user WHERE `telegram_id` = %s" % userId)
            if len(userResult) > 0:
                await context.bot.edit_message_text('%s\n你已经绑定过账号了！' % bot.text["fail"],chatId,msgId)
                return
            # 该 token 是否在库
            subResult = onQuery("SELECT * FROM v2_user WHERE `token` = '%s'" % subInfo[1])
            if len(subResult) == 0:
                await context.bot.edit_message_text('%s\n请输入正确的订阅链接！' % bot.text["fail"],chatId,msgId)
                return
            elif len(subResult) > 1:
                await context.bot.edit_message_text('%s\n绑定错误！' % bot.text["fail"],chatId,msgId)
                return
            else:
                if subResult[0][2] is not None:
                    await context.bot.edit_message_text('%s\n这个账号已绑定到别的 Telegram 了！' % bot.text["fail"],chatId,msgId)
                    return
                else:
                    db = MysqlUtils(port=bot.port)
                    db.update_one('v2_user',{'telegram_id': userId},{'token': subInfo[1]})
                    db.conn.commit()
                    db.close()
                    await context.bot.edit_message_text('%s\n你已成功绑定 Telegram 了！' % bot.text["okay"],chatId,msgId)
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