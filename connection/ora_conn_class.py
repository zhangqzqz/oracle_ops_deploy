# -*- coding:utf-8 -*-
import logging

import cx_Oracle

# logging
logging.basicConfig(
    format="%(levelname)s\t%(asctime)s\t%(message)s", filename="ora_ops.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ConnectOracle():
    def __init__(self,db_args,mode):
        self.ora_ip,self.ora_user,self.ora_port,self.ora_pwd,self.ora_sid = db_args
        self.ora_port = int(self.ora_port)
        self.mode = mode

    def get_connect(self):
        try:
            if self.mode.upper() == 'SYSDBA':
                self.conn = cx_Oracle.connect(f"{self.ora_user}/{self.ora_pwd}@{self.ora_ip}/{self.ora_sid}:{self.ora_port}",encoding="UTF-8",mode=cx_Oracle.SYSDBA)
            else:
                self.conn = cx_Oracle.connect(f"{self.ora_user}/{self.ora_pwd}@{self.ora_ip}/{self.ora_sid}:{self.ora_port}",encoding="UTF-8",mode=cx_Oracle.DEFAULT_AUTH)
            logger.debug("[%s] oracle db connect: ok",self.ora_ip)
        except Exception as err:
            logger.debug("[%s] oracle db connect: error\n%s",
                        self.ora_ip,err)
            print("[%s] oracle db connect: error\n%s",
                        self.ora_ip,err)
    def get_cur(self):
        return self.conn.cursor()

    def close_db(self):
        self.cursor.close()
        self.conn.close()
        logger.debug("[%s] ora db close: ok", self.ora_ip)


    def ora_all(self,sql):
        try:
            self.get_connect()
            self.cursor = self.get_cur()
            self.cursor.execute(sql)
            res = list(self.cursor.fetchall())
            res.sort()
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, sql)
            logger.debug("[%s] result: %s", self.ora_ip, res)
            title = [i[0] for i in self.cursor.description]
            return res,title
        except Exception as err:
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, sql)
            logger.debug("[%s] result: %s", self.ora_ip, err)
            print(f"ERROR:\n{sql}: Failed.\n{err}\n")
            return f"{sql}: Failed.\n {err}\n"
        finally:
            self.close_db()



    def ora_no_fetch(self, sql):

        try:
            self.get_connect()
            self.cursor = self.get_cur()
            self.cursor.execute(sql)
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, sql)
            logger.debug("[%s]", self.ora_ip)

            return 'exec s'
        except Exception as err:
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, sql)
            logger.debug("[%s] result: %s", self.ora_ip, err)
            print(f"ERROR:\n{sql}: Failed.\n{err}\n")
            return f"{sql}: Failed.\n {err}\n"
        finally:
            self.conn.commit()
            self.close_db()

    def ora_func(self,func_name,func_var):
        try:
            self.get_connect()
            self.cursor=self.get_cur()
            res = self.cursor.callfunc("DBMS_METADATA.GET_DDL", str,[func_name, func_var])
            
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, func_name)
            logger.debug("[%s] result: %s", self.ora_ip, res)
            return res
        except Exception as err:
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, func_name)
            logger.debug("[%s] result: %s", self.ora_ip, err)
            print(f"ERROR:\n{func_name}: Failed.\n{err}\n")
            return f"{func_name}: Failed.\n {err}\n"
        finally:
            self.close_db()


    def ora_no_fetch_more(self, sqls):
        try:
            self.get_connect()
            self.cursor = self.get_cur()
            for sql in sqls:
                self.cursor.execute(sql)
            logger.debug("[%s] sqls: %s \nexecute: ok",
                        self.ora_ip, sqls)
            logger.debug("[%s]", self.ora_ip)

            return 'exec s'
        except Exception as err:
            logger.debug("[%s] sqls: %s \nexecute: ok",
                        self.ora_ip, sqls)
            logger.debug("[%s] result: %s", self.ora_ip, err)
            print(f"ERROR:\n{''.join(sqls)}: Failed.\n{err}\n")
            return f"{sqls}: Failed.\n {err}\n"
        finally:
            self.conn.commit()
            self.close_db()


    def ora_proc_use(self, proc_name,args_list):
        sql =''
        try:
            self.get_connect()
            self.cursor = self.get_cur()
            # inOutArrayVar = cursor.arrayvar(str, [args_list[1]])
            res = self.cursor.callproc(proc_name,args_list)
    
            # sql = ''
        # sql = f"begin {func_name}({','.join([':'+str(i+1) for i in list(range(len(args_list)))])}); end;"
        #  sql = f"begin DBMS_LOGMNR.ADD_LOGFILE(logfilename => '{args_list[0]}',options => dbms_logmnr.new); end;"

            #res = cursor.execute(sql)
            logger.debug("[%s] oracle db connect: ok",self.ora_ip)
            
            
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, sql)
            logger.debug("[%s] result: %s", self.ora_ip, res)
            return res
        except Exception as err:
            logger.debug("[%s] sql: %s \nexecute: ok",
                        self.ora_ip, sql)
            logger.debug("[%s] result: %s", self.ora_ip, err)
            print(f"ERROR:\n{sql}: Failed.\n{err}\n")
            return f"{sql}: Failed.\n {err}\n"
        finally:
            self.close_db()
