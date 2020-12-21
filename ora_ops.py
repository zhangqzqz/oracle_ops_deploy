#!/usr/bin/env python
import argparse
import functools
import json
import logging
import sys


from method import check_instance,create_dir,parse_conn
from ora_expdp.ora_expdp import expdp
from ora_lock.lock_tool import lock_ops
from ora_expdp_cron.ora_expdp_cron import expdp_cron
from ora_clean_log.ora_clean_log import ora_clean_log
from ora_logmnr.logmnr import logmnr_run
from ora_tbs_check.ora_tbs_check import ora_tbs_check
from ora_drop_tables.ora_drop_tables import ora_drop_tables
from ora_service_set.ora_service_set import ora_service_set
from configparse.config_parse import get_config,get_expdp_config,get_expdp_cron_config,get_section_config

# global

__version__ = "1.1.0"


# logging

logging.basicConfig(
    format="%(levelname)s\t%(asctime)s\t%(message)s", filename="ora_ops.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# main

def main():

    parser = argparse.ArgumentParser(description="oracle ops")
    parser.add_argument("-m","--mode",type=str,default='default_auth',
                        help="数据库连接方式，可填'sysdba'或'default_auth',默认为'default_auth'")
    # parser.add_argument("-u","--user",type=str,
    #                     help="操作系统oracle用户")
    # parser.add_argument("-p","--password",type=str,
    #                     help="操作系统oracle用户密码")
    # parser.add_argument("-P","--ssh_port",type=int,
    #                     help="操作系统ssh的端口号")
    # parser.add_argument("-d","--degree",type=int,
    #                     help="导入导出时的并行度")
    # parser.add_argument("-path","--path",type=str,
    #                     help="导入导出文件存放路径")
    # parser.add_argument("-db_path","--datafile_path",type=str,
    #                     help="生成导入库初始化表空间时用到的数据文件存放路径")
    # parser.add_argument("-s","--sync_obj",type=str,
    #                     help="想要导出的对象，例如，全库：full_expdp | 多用户：test,test1 | 多表：test.t1,test.t2,test2.t10")
    # parser.add_argument("-ftp_ip","--ftp_ip",type=str,
    #                     help="使用ftp服务时远端服务器的ip地址")
    # parser.add_argument("-ftp_dir","--ftp_dir",type=str,
    #                     help="使用ftp时远端服务器的路径")
    # parser.add_argument("-ftp_user","--ftp_user",type=str,
    #                     help="使用ftp服务时远端服务器的用户名")
    # parser.add_argument("-ftp_passwd","--ftp_passwd",type=str,
    #                     help="使用ftp服务时远端服务器的用户密码")
    parser.add_argument("-r","--retention_day",type=str,default=30,
                        help="数据库日志本地保留时间天数")  
            
    # parser.add_argument("-crontab_date","--crontab_date",type=str,
    #                     help="调用crontab时的定时参数设置,一般格式为:<分 时 日 月 周>,详细写法参考crontab写法")            
    parser.add_argument("-i","--item",choices=['check_instance','expdp','create_dir','check_lock','expdp_crontab','clean_log','logmnr','tbs_check','service_set','drop_tables'],required=True,
                        help="expdp:数据库导出|check_instance:检查数据库|create_dir:创建数据库导入导出目录|check_lock:TX锁检查|clean_log:数据库日志情况|expdp_crontab:设置逻辑泵备份任务|logmnr:日志挖掘功能\
                        |tbs_check:表空间空间检查|service_set:设置数据库服务自启动|drop_tables:生成用户下批量快速删除表对象的脚本")

    args = parser.parse_args()
    mode = args.mode
    item = args.item
    # sys_user = args.user
    # sys_passwd = args.password
    # sync_obj = args.sync_obj
    # ssh_port = args.ssh_port
    # degree = args.degree
    # path  = args.path
    # dbf_path = args.datafile_path
    # ftp_ip = args.ftp_ip
    # ftp_dir = args.ftp_dir
    # ftp_user = args.ftp_user
    # ftp_passwd = args.ftp_passwd
    retention_day = args.retention_day

    # crontab_date_str = args.crontab_date

    db_args,os_args = get_config()
    host,os_port,os_username,os_password = os_args
    if item == "check_instance":
        check_instance(db_args,mode)
    elif item == "expdp":
        
        exp_args,tag_os_args = get_expdp_config()
        degree,path,dbf_path,sync_obj,tag_dmp_path = exp_args
        expdp(db_args,sync_obj,os_username,os_password,mode,os_port,degree,path,dbf_path,tag_os_args,tag_dmp_path)
    elif item == "create_dir":
        create_dir(db_args,mode,os_args,path)
    elif item == "check_lock":
        lock_ops(db_args,mode)
    elif item == "expdp_crontab":
        cron_args = get_expdp_cron_config()
        degree,dmp_path,ftp_ip,ftp_dir,ftp_user,ftp_passwd,crontab_date_str,retention_day,sync_obj = cron_args
        expdp_cron(db_args,sync_obj,os_username,os_password,mode,os_port,degree,dmp_path,ftp_ip,ftp_dir,ftp_user,ftp_passwd,crontab_date_str,retention_day)
    elif item == "clean_log":
        if os_username != 'root':
            print('WARNING:操作系统用户需为root!')
            return 0
        else:
            ora_clean_log(os_args,retention_day)
    elif item == 'logmnr':
        logmnr_dict = get_section_config('logmnr_config')
        logmnr_run(db_args,mode,logmnr_dict)
    elif item == 'tbs_check':
        y_n = input("请确认您config.cfg配置中填写的是oracle用户及密码: y/n ")
        if y_n.upper()=='Y':
            sid = input("请输入您要检查的数据库环境的sid： ")
            ora_tbs_check(os_args,sid)
        else:
            pass
    elif item == 'service_set':
        if os_username != 'root':
            print('WARNING:操作系统用户需为root!')
            return 0
        else:
            ora_service_set(os_args)
    elif item == 'drop_tables':
        y_n = input("请确认您config.cfg 配置中填写的是oracle用户及密码: y/n ")
        if y_n.upper()=='Y':
            drop_tables_dict = get_section_config('drop_tables')
            ora_drop_tables(os_args,drop_tables_dict)
        else:
            pass




    

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
