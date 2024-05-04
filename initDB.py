import logging
import os
from handler import MysqlUtils
import bot

class Conf:
    desc = '初始化数据库'
    method = 'once'
    interval = 60


config = bot.config['bot']
sqlScripts = []


def onQuery(sql):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


def isExistTable(tableName):
    try:
        db = MysqlUtils(port=bot.port)
        result = db.is_exist_table(tableName)
        return result
    except Exception as err:
        return False
    finally:
        db.close()


def initDatabase():

    try:
        logging.info(f'Bot-Databases-Module: 数据库初始化中...')
        isExistModulesTable = isExistTable('bot_modules')
        sqlScriptDir = "./Databases/"
        for root, dirs, files in os.walk(sqlScriptDir):
            files.sort()
            for file in files:
                if isExistModulesTable and str(root).find('/Databases/01_init') > 0:
                    continue
                fullname = os.path.abspath(os.path.join(root, file))
                sqlScripts.append(fullname)

        if isExistModulesTable:
            initedModules = onQuery("SELECT module FROM bot_modules")
            if len(initedModules) != 0:
                for i in range(len(initedModules)):
                    for j in range(len(sqlScripts)-1, -1, -1):
                        if str(sqlScripts[j]).find(str(initedModules[i][0]).split('.')[1]) < 0:
                            continue
                        else:
                            del sqlScripts[j]
    except Exception as err:
        logging.warning(f'Bot-Databases-Module: 数据库初始化错误 - {err}')

    if len(sqlScripts) > 0:
        try:
            logging.info(f'Bot-Databases-Module: 数据库脚本执行中...')
            db = MysqlUtils(port=bot.port)
            for sqlScript in sqlScripts:
                with open(sqlScript) as sqlFile:
                    sqlScriptContents = sqlFile.read().splitlines()
                    for sqlScriptContent in sqlScriptContents:
                        db.cur.execute(sqlScriptContent)
                        db.conn.commit()
            logging.info(f'Bot-Databases-Module: 数据库脚本执行完毕...')
        except Exception as err:
            logging.warning(f'Bot-Databases-Module: 数据库脚本执行错误 - {err}')
        finally:
            db.close()



initDatabase()
