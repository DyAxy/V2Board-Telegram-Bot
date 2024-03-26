from telegram import Update
from telegram.ext import ContextTypes
desc = '开始使用 Bot'


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    chat_type = update.effective_chat.type

    if chat_type == 'private':
        await msg.reply_markdown('欢迎使用这个Bot，绑定请输入 /bind 订阅地址')
