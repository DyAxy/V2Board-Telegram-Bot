import logging
from handler import MysqlUtils
from telegram import Update
from telegram.ext import ContextTypes

import bot
desc = '获取我的邀请信息'
config = bot.config['bot']


def onQuery(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.sql_query(sql)
    finally:
        db.close()
        return result
    

def getContent(uid:int)->str:
    code = onQuery('SELECT code FROM v2_invite_code WHERE user_id = %s' % uid)
    if len(code) == 0:
        return '%s\n你还没有生成过邀请码！' % bot.text["fail"]
    
    count = onQuery('SELECT id FROM v2_user WHERE invite_user_id = %s' % uid)
    flow = [
        '📚<b>邀请信息</b>',
        '',
        '🔮邀请地址为（点击即可复制）：'
        '<code>%s/#/register?code=%s</code>' % (config['website'], code[0][0]),
        '',
        '👪<b>邀请人数：</b> %s' % len(count)
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
            user = onQuery('SELECT id FROM v2_user WHERE `telegram_id` = %s' % userId)
            if chatType != 'private':
                context.job_queue.run_once(
                    bot.autoDelete, config["delete_time"], data=msg.id, chat_id=chatId, name=str(msg.id))
                context.job_queue.run_once(
                    bot.autoDelete, config["delete_time"], data=callback.message_id, chat_id=chatId, name=str(callback.message_id))
            if len(user) == 0:
                await context.bot.edit_message_text('%s\n你还没有绑定过账号！' % bot.text["fail"],chatId,msgId)
                return
            else:
                text = getContent(user[0][0])
                await context.bot.edit_message_text(text,chatId,msgId)
        except Exception as error:
            logging.warning(error)
            await context.bot.edit_message_text('%s\n查询出现异常，请稍后再试！' % bot.text["fail"],chatId,msgId)
            return 