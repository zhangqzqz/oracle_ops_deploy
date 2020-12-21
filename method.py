# -*- coding:utf-8 -*-
import functools
import re
import logging

from prettytable import PrettyTable,ALL

from connection.ora_conn import ora_all,ora_no_fetch
from connection.ora_conn_class import ConnectOracle
from connection.ssh_input import ssh_input_noprint

# logging
logging.basicConfig(format="%(levelname)s\t%(asctime)s\t%(message)s",filename="ora_conn.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Decorator
def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('\ncall %s():' % func.__name__)
        return func(*args, **kwargs)
    return wrapper

# put res to a prettytable
@log
def res_table(res,title):
    t= PrettyTable(title)
    t.hrules = ALL
    for i in res:
        i = list(i)
        for index,m in enumerate(i):
            if isinstance(m,str):
                if len(m) > 100:
                    n = re.findall(r'.{50}',m)
                    m = '\n'.join(n)
                    i[index] = m
        t.add_row(i)

    return t


# check instance
# @log
# def check_instance(db_args,mode):
#     check_instance_status_sql = "select INST_ID,INSTANCE_NAME,STATUS,VERSION from gv$instance "
#     check_instance_res,title = ora_all(db_args,check_instance_status_sql,mode)
#     print("\n###检查数据库信息:")
#     instance_table = res_table(check_instance_res,title)
#     print(instance_table)
#     return 0

@log
def check_instance(db_args,mode):
    check_instance_status_sql = "select INST_ID,INSTANCE_NAME,STATUS,VERSION from gv$instance "
    mydb = ConnectOracle(db_args,mode)
    check_instance_res,title = mydb.ora_all(check_instance_status_sql)
    print("\n###检查数据库信息:")
    instance_table = res_table(check_instance_res,title)
    print(instance_table)
    return 0
# check db
@log
def check_db(db_args,mode):
    check_instance_sql = f"select INST_ID,INSTANCE_NAME,STATUS,VERSION from gv$instance"
    ins_res,ins_title = ora_all(db_args,check_instance_sql,mode)
    print(f"\nINFO:检查数据库信息 {db_args[0]}:")
    db_table = res_table(ins_res,ins_title)
    print(db_table)
    return 0

# parse the string for conn
@log
def parse_conn(conn_str):
    args = re.split('[/@:]',conn_str)
    return args
    

# get sid of oracle
@log 
def get_sid(conn_str,mode):
    get_sid_sql = "select instance_name from v$instance"
    sid,_ = ora_all(conn_str,get_sid_sql,mode)
    sid = sid[0][0]
    return sid

# get whether or not the rac is
@log
def get_rac_state(conn_str,mode):
    get_rac_sql = "SELECT value FROM v$parameter where name = 'cluster_database'"
    rac,_ = ora_all(conn_str,get_rac_sql,mode)
    rac = rac[0][0]
    return rac

# create the directory for expdp or impdp
@log
def create_dir(db_args,mode,os_args,path):

    dmp_dir = path

    check_dir_res = ''.join(ssh_input_noprint(os_args,f"ls {dmp_dir}"))
    if 'No such file or directory' in check_dir_res:
        print("\nWARRING:该路径不存在，请检查系统环境！")
        return 0
    create_sql = f"create or replace directory mc_dump_dir as '{dmp_dir}'"
    grant_sql = f"grant read,write on directory mc_dump_dir to public"
    check_sql = "select * from dba_directories where DIRECTORY_NAME = 'MC_DUMP_DIR'"
    create_dir_res = ora_no_fetch(db_args, create_sql, mode)
    ora_no_fetch(db_args,grant_sql,mode)
    if 'fail' not in create_dir_res:
        check_res,check_title = ora_all(db_args,check_sql,mode)
        t = res_table(check_res,check_title)
        print(f"\nINFO:{db_args[0]} \n数据库目录MC_DUMP_DIR：{dmp_dir} 创建成功")
        print (t)
        
        return 'create dir s'
    else:
        return 'create dir f'