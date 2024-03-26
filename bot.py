
import os
import yaml
import logging

from datetime import time
from sshtunnel import SSHTunnelForwarder

from handler import MysqlUtils

from telegram import BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes,Defaults

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)


text = {
    "okay": "✔️<b>成功</b>",
    "fail": "❌<b>错误</b>",
}

# Load Config
try:
    f = open('config.yml', 'r')
    config = yaml.safe_load(f)
except FileNotFoundError as error:
    logging.warning('没有找到 config.yml，请复制 config.yml.example 并重命名为 config.yml')
    exit(1)

# Connect SSH
try:
    sshInfo = config['v2board']['ssh']
    sqlInfo = config['v2board']['database']
    port = sqlInfo['port']
    if sshInfo['enable'] is True:
        sshParams = {
            'ssh_address_or_host': (sshInfo['ip'], sshInfo['port']),
            'ssh_username': sshInfo['user'],
            'remote_bind_address': (sqlInfo['ip'], sqlInfo['port'])
        }
        if sshInfo['type'] == "passwd":
            sshParams['ssh_password'] = sshInfo['pass']
        if sshInfo['type'] == "pkey":
            sshParams['ssh_pkey'] = sshInfo['keyfile']
            sshParams['ssh_private_key_password'] = sshInfo['keypass']

        ssh = SSHTunnelForwarder(**sshParams)
        ssh.start()
        port = ssh.local_bind_port
except Exception as error:
    logging.warning('你已启用 SSH，但是 SSH 的相关配置不正确')
    exit(1)

# Test Mysql Connection
try:
    db = MysqlUtils(port=port)
    db.close()
except Exception as error:
    logging.warning(error)
    exit(1)


async def autoDelete(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        job = context.job
        await context.bot.delete_message(job.chat_id, job.data)
    except Exception as error:
        logging.info(error)

async def setCommand(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands()
    await context.bot.set_my_commands(context.job.data)
    

def main():
    try:
        app = Application.builder().token(config['bot']['token']).defaults(Defaults(parse_mode='HTML')).build()
        # 导入命令文件夹
        import Commands
        command_list = []
        for i in Commands.content:
            cmds = getattr(Commands, i)
            app.add_handler(CommandHandler(i, cmds.exec))
            command_list.append(BotCommand(i, cmds.desc))
        app.job_queue.run_once(setCommand, 1, command_list, 'setCommand')
        # 导入任务文件夹
        import Modules
        for i in Modules.content:
            mods = getattr(Modules, i)
            Conf = mods.Conf
            if Conf.method == 'daily':
                app.job_queue.run_daily(
                    mods.exec, time.fromisoformat(Conf.runtime), name=i)
            elif Conf.method == 'repeating':
                app.job_queue.run_repeating(
                    mods.exec, interval=Conf.interval, name=i)
        # 启动 Bot
        if os.getenv('RUNNER_NAME') is not None:
            return
        app.run_polling(drop_pending_updates=True)
    except Exception as error:
        logging.warning('无法启动 Telegram Bot，请确认 Bot Token 是否正确，或者是否能连接 Telegram 服务器')
        exit(1)


if __name__ == "__main__":
    main()
