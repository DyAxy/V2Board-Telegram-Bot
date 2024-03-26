from telegram import Update
from telegram.ext import ContextTypes

import bot
desc = '获取当前聊天信息'
config = bot.config['bot']


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    userId = msg.from_user.id
    chatId = msg.chat_id
    chatType = msg.chat.type

    callback = await msg.reply_text("请稍等...")
    msgId = callback.message_id

    flow = [
        '💥<b>嘭</b>',
        '你的ID为：<code>%s</code>' % userId,
    ]
    if chatType != 'private':
        flow.append('群组ID为：<code>%s</code>' % chatId)
        context.job_queue.run_once(
                bot.autoDelete, config["delete_time"], data=msg.id, chat_id=chatId, name=str(msg.id))
        context.job_queue.run_once(
                bot.autoDelete, config["delete_time"], data=callback.message_id, chat_id=chatId, name=str(callback.message_id))

    await context.bot.edit_message_text('\n'.join(flow),chatId,msgId)