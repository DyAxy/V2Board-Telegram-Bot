import logging
from handler import MysqlUtils
import time
from telegram.ext import ContextTypes

import bot


class Conf:
    desc = '推送新订单'
    method = 'repeating'
    interval = 60


config = bot.config['bot']
order_total = 0
order_status = []
thisEnhanced = False

mapping = {
    'Type': ['无', '新购', '续费', '升级', '重置'],
    'Period': {
        'month_price': '月付',
        'quarter_price': '季付',
        'half_year_price': '半年付',
        'year_price': '年付',
        'two_year_price': '两年付',
        'three_year_price': '三年付',
        'onetime_price': '一次性',
        'reset_price': '重置包',
    }
}


def fmtTime(timestamp: float) -> str:
    tFormat = "%Y-%m-%d %H:%M:%S"
    return time.strftime(tFormat, time.localtime(timestamp))


def addEscapeChar(string):
    reserved_chars = '''\\`*_{}[]()#+.!|'''
    replace = ['\\' + l for l in reserved_chars]
    trans = str.maketrans(dict(zip(reserved_chars, replace)))
    return string.translate(trans)


def onQuery(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.sql_query(sql)
    except Exception as err:
        logging.warning(err)
    finally:
        db.close()
        return result


def onSqlExec(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.execute_sql(sql)
        if result is not None:
            raise Exception(result)
    except Exception as err:
        logging.warning(err)
    finally:
        db.close()


def onSqlInsertMany(table: str, attrs: list, values: list):
    try:
        db = MysqlUtils(port=bot.port)
        db.insert_many(table, attrs, values)
    except Exception as err:
        logging.warning(err)
    finally:
        db.close()


def onUpdate(tableName, params, conditions):
    try:
        db = MysqlUtils(port=bot.port)
        db.update_one(tableName, params, conditions)
    except Exception as err:
        logging.warning(err)
    finally:
        db.close()


async def getUnNotifyValidOrders():
    try:
        validOrders = onQuery('SELECT `id`,1,0 FROM v2_order WHERE v2_order.total_amount<>0 AND v2_order.`status`=3 AND NOT EXISTS(SELECT order_id from bot_modules_notify WHERE bot_modules_notify.order_id=v2_order.id AND bot_modules_notify.type=1) ORDER BY `id` ASC')
        if len(validOrders) > 0:
            onSqlInsertMany(
                'bot_modules_notify', ["order_id", "type", "state"], validOrders)

        unNotifyValidOrders = onQuery('SELECT v2_user.email,t_plan.`name`,t_payment.`name`,t_order.type,t_order.period,t_order.total_amount,t_order.paid_at,t_notify.id,t_notify.state FROM bot_modules_notify AS t_notify INNER JOIN v2_order AS t_order ON t_notify.order_id=t_order.id INNER JOIN v2_plan AS t_plan ON t_order.plan_id=t_plan.id INNER JOIN v2_payment AS t_payment ON t_order.payment_id=t_payment.id INNER JOIN v2_user ON t_order.user_id=v2_user.id WHERE t_notify.state=0 AND t_notify.type=1')
        if len(unNotifyValidOrders) > 0:
            return unNotifyValidOrders
        else:
            return None
    except Exception as err:
        logging.warning(err)


def buildMsg(row) -> str:

    flow = [
        f"<b>📠新的订单</b>",
        f"",
        f"<b>📧注册邮箱:</b> {row[0]}",
        f"<b>📚套餐名称:</b> {row[1]}",
        f"<b>💵支付方式:</b> {row[2]}",
        f"<b>📥套餐类型:</b> {mapping['Type'][row[3]]}",
        f"<b>📅套餐时长:</b> {mapping['Period'][row[4]]}",
        f"<b>🏷套餐价格:</b> {round(row[5]/100, 2)}",
        f"<b>🕰支付时间:</b> {fmtTime(row[6])}"
    ]
    return '\n'.join(flow)


async def exec(context: ContextTypes.DEFAULT_TYPE):
    try:
        rows = await getUnNotifyValidOrders()
        if rows is not None:
            print(len(rows))
            for row in rows:
                text = buildMsg(row)
                for adminID in config['admin_id']:
                    print(text)
                    await context.bot.send_message(adminID, text)
                onUpdate('bot_modules_notify', {'state': 1}, {'id': row[7]})
    except Exception as error:
        logging.warning(error)
