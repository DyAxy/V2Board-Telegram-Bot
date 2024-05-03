import bot
import pytz
import datetime
import calendar
import logging
from handler import MysqlUtils
from telegram.ext import ContextTypes


timezone = pytz.timezone('Asia/Shanghai')


class Conf:
    desc = '定时推送用量'
    method = 'daily'
    # V2board 1.7.4
    runtime = '00:15:00+08:00'


class Settings:
    # 服务器统计
    send_server = True
    # 用户统计
    send_user = True
    # 统计多少个
    index = 5
    # 订单统计（仅推送admin）
    send_order = True


config = bot.config['bot']


def onQuery(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.sql_query(sql)
    except Exception as err:
        logging.error(err)
    finally:
        db.close()
        return result


def getTimestemp():
    yesterday = (datetime.datetime.now(timezone) -
                 datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    inconvert = datetime.datetime.strptime(yesterday, "%Y-%m-%d")
    timestemp = int(calendar.timegm(inconvert.timetuple())-28800)
    return timestemp


def onSendServer():
    result = onQuery(
        "SELECT server_id,server_type,u,d FROM v2_stat_server WHERE record_at = %s" % getTimestemp())
    result_list = []
    if result is not None and len(result) > 0:
        for i in result:
            result_list.append(i)
        result_list.sort(key=lambda x: x[3], reverse=True)
        index = Settings.index
        if len(result_list) < index:
            index = len(result_list)
        text = f'使用的前 {index} 的节点：\n\n'
        for i in range(index):
            tbl_name = f'v2_server_{result_list[i][1]}'
            node_name = onQuery(
                f"SELECT name FROM {tbl_name} WHERE id = {result_list[i][0]}")[0][0]
            download = round(
                (result_list[i][2] + result_list[i][3]) / 1024 / 1024 / 1024, 2)
            text = f'{text}{node_name} - `{download}` GB\n'
        return text
    else:
        return ''


def onSendUser():
    result = onQuery(
        "SELECT user_id,u,d FROM v2_stat_user WHERE record_at = %s" % getTimestemp())
    result_dict = {}
    if result is not None and len(result) > 0:
        for i in result:
            if str(i[0]) not in result_dict:
                result_dict[str(i[0])] = i[1] + i[2]
            else:
                result_dict[str(i[0])] += i[1] + i[2]
        result_list = sorted(result_dict.items(),
                             key=lambda x: x[1], reverse=True)
        index = Settings.index
        if len(result_list) < index:
            index = len(result_list)
        text = f'流量使用前 {index} 名用户：\n\n'
        for i in range(index):
            user = onQuery("SELECT * FROM v2_user WHERE id = %s" %
                           result_list[i][0])
            total = round(result_list[i][1] / 1024 / 1024 / 1024, 2)
            text = f'{text}`***@***.com` - #`{user[0][0]}` - `{total}` GB\n'
        return text
    else:
        return ''


def onSendOrder():
    result = onQuery(
        "SELECT order_count,order_amount,commission_count,commission_amount FROM v2_stat_order WHERE record_at = %s" % getTimestemp())
    if result is not None and len(result) > 0:
        order_count = result[0][0]
        order_amount = round(result[0][1] / 100, 2)
        commission_count = result[0][2]
        commission_amount = round(result[0][3] / 100, 2)
        text = ''
        text = f'{text}📑*订单总数*：{order_count} 单\n'
        text = f'{text}💰*订单金额*：{order_amount} 元\n'
        text = f'{text}💸*返现次数*：{commission_count} 单\n'
        text = f'{text}💵*返现金额*：{commission_amount} 元\n'
        return text
    else:
        return ''


def onTodayData():
    text = '📊*昨日统计：*\n\n'
    if Settings.send_server is True:
        text = f'{text}{onSendServer()}\n'
    if Settings.send_user is True:
        text = f'{text}{onSendUser()}\n'
    if Settings.send_server is False and Settings.send_user is False:
        return False, ''
    else:
        return True, text


def onTodayOrderData():
    content = onSendOrder()
    if Settings.send_order is False or len(content) == 0:
        return False, ''
    elif Settings.send_order is True:
        text = f'📊*昨日统计：*\n\n{content}\n'
        return True, text


async def exec(context: ContextTypes.DEFAULT_TYPE):
    result, text = onTodayData()
    if result is True:
        await context.bot.send_message(
            chat_id=config['group_id'],
            text=text,
            parse_mode='Markdown'
        )
    result, text = onTodayOrderData()
    if result is True:
        for admin_id in config['admin_id']:
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode='Markdown'
            )
