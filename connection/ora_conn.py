# -*- coding:utf-8 -*-
import logging

import cx_Oracle

# logging
logging.basicConfig(
    format="%(levelname)s\t%(asctime)s\t%(message)s", filename="ora_ops.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def ora_all(db_args, sql, mode):
    #conn_str_log = conn_str.split('@')[1]
    # conn_string = f"{ora_ip}:{ora_port}/{ora_service_name}"
    ora_ip,ora_user,ora_port,ora_pwd,ora_sid = db_args
    ora_port = int(ora_port)

    try:
        if mode.upper() == 'SYSDBA':
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.SYSDBA)
        else:
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.DEFAULT_AUTH)
        cursor = conn.cursor()
        logger.debug("[%s] oracle db connect: ok",ora_ip)
        cursor.execute(sql)
        res = list(cursor.fetchall())
        res.sort()
        logger.debug("[%s] sql: %s \nexecute: ok",
                     ora_ip, sql)
        logger.debug("[%s] result: %s", ora_ip, res)
        title = [i[0] for i in cursor.description]
        return res,title
    except Exception as err:
        logger.debug("[%s] sql: %s \nexecute: ok",
                    ora_ip, sql)
        logger.debug("[%s] result: %s", ora_ip, err)
        print(f"ERROR:\n{sql}: Failed.\n{err}\n")
        return f"{sql}: Failed.\n {err}\n"
    finally:
        cursor.close()
        conn.close()
        logger.debug("[%s] ora db close: ok", ora_ip)

def ora_no_fetch(db_args, sql, mode):
    # conn_string = f"{ora_ip}:{ora_port}/{ora_service_name}"
    # conn_str_log = conn_str.split('@')[1]
    ora_ip,ora_user,ora_port,ora_pwd,ora_sid = db_args
    ora_port = int(ora_port)
    try:
        if mode.upper() == 'SYSDBA':
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.SYSDBA)
        else:
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.DEFAULT_AUTH)
        
        cursor = conn.cursor()

        logger.debug("[%s] oracle db connect: ok",ora_ip)
        cursor.execute(sql)
        logger.debug("[%s] sql: %s \nexecute: ok",
                     ora_ip, sql)
        logger.debug("[%s]", ora_ip)

        return 'exec s'
    except Exception as err:
        logger.debug("[%s] sql: %s \nexecute: ok",
                    ora_ip, sql)
        logger.debug("[%s] result: %s", ora_ip, err)
        print(f"ERROR:\n{sql}: Failed.\n{err}\n")
        return f"{sql}: Failed.\n {err}\n"
    finally:
        cursor.close()
        conn.commit()
        conn.close()
        logger.debug("[%s] ora db close: ok", ora_ip)

def ora_func(db_args, func_name,func_var, mode):
  #  conn_str_log = conn_str.split('@')[1]
    # conn_string = f"{ora_ip}:{ora_port}/{ora_service_name}"
    ora_ip,ora_user,ora_port,ora_pwd,ora_sid = db_args
    ora_port = int(ora_port)
    try:
        if mode.upper() == 'SYSDBA':
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.SYSDBA)
        else:
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.DEFAULT_AUTH)
        cursor = conn.cursor()
        res = cursor.callfunc("DBMS_METADATA.GET_DDL", str,[func_name, func_var])
        logger.debug("[%s] oracle db connect: ok",ora_ip)
        
        
        logger.debug("[%s] sql: %s \nexecute: ok",
                     ora_ip, func_name)
        logger.debug("[%s] result: %s", ora_ip, res)
        return res
    except Exception as err:
        logger.debug("[%s] sql: %s \nexecute: ok",
                    ora_ip, func_name)
        logger.debug("[%s] result: %s", ora_ip, err)
        print(f"ERROR:\n{func_name}: Failed.\n{err}\n")
        return f"{func_name}: Failed.\n {err}\n"
    finally:
        cursor.close()
        conn.close()
        logger.debug("[%s] ora db close: ok", ora_ip)


def ora_no_fetch_more(db_args, sqls, mode):
    # conn_string = f"{ora_ip}:{ora_port}/{ora_service_name}"
    # conn_str_log = conn_str.split('@')[1]
    ora_ip,ora_user,ora_port,ora_pwd,ora_sid = db_args
    ora_port = int(ora_port)
    try:
        if mode.upper() == 'SYSDBA':
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.SYSDBA)
        else:
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.DEFAULT_AUTH)
        
        cursor = conn.cursor()

        logger.debug("[%s] oracle db connect: ok",ora_ip)
        for sql in sqls:
            cursor.execute(sql)
        logger.debug("[%s] sqls: %s \nexecute: ok",
                     ora_ip, sqls)
        logger.debug("[%s]", ora_ip)

        return 'exec s'
    except Exception as err:
        logger.debug("[%s] sqls: %s \nexecute: ok",
                    ora_ip, sqls)
        logger.debug("[%s] result: %s", ora_ip, err)
        print(f"ERROR:\n{''.join(sqls)}: Failed.\n{err}\n")
        return f"{sqls}: Failed.\n {err}\n"
    finally:
        cursor.close()
        conn.commit()
        conn.close()
        logger.debug("[%s] ora db close: ok", ora_ip)


def ora_proc_use(db_args, proc_name,args_list, mode):
  #  conn_str_log = conn_str.split('@')[1]
    # conn_string = f"{ora_ip}:{ora_port}/{ora_service_name}"
    ora_ip,ora_user,ora_port,ora_pwd,ora_sid = db_args
    ora_port = int(ora_port)
    sql =''
    try:
        if mode.upper() == 'SYSDBA':
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.SYSDBA)
        else:
            conn = cx_Oracle.connect(f"{ora_user}/{ora_pwd}@{ora_ip}/{ora_sid}:{ora_port}",encoding="UTF-8",mode=cx_Oracle.DEFAULT_AUTH)
        cursor = conn.cursor()
        # inOutArrayVar = cursor.arrayvar(str, [args_list[1]])
        res = cursor.callproc(proc_name,args_list)
  
        # sql = ''
       # sql = f"begin {func_name}({','.join([':'+str(i+1) for i in list(range(len(args_list)))])}); end;"
      #  sql = f"begin DBMS_LOGMNR.ADD_LOGFILE(logfilename => '{args_list[0]}',options => dbms_logmnr.new); end;"

        #res = cursor.execute(sql)
        logger.debug("[%s] oracle db connect: ok",ora_ip)
        
        
        logger.debug("[%s] sql: %s \nexecute: ok",
                     ora_ip, sql)
        logger.debug("[%s] result: %s", ora_ip, res)
        return res
    except Exception as err:
        logger.debug("[%s] sql: %s \nexecute: ok",
                    ora_ip, sql)
        logger.debug("[%s] result: %s", ora_ip, err)
        print(f"ERROR:\n{sql}: Failed.\n{err}\n")
        return f"{sql}: Failed.\n {err}\n"
    finally:

        cursor.close()
        conn.close()
        logger.debug("[%s] ora db close: ok", ora_ip)

