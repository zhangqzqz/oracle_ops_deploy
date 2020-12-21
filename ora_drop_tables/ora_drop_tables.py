#!/usr/bin/env python

import sys
from ora_expdp_cron.ora_expdp_cron_method import crontab_config,estimate_size_expdp,get_expdp_str
from method import parse_conn,log,check_db,log,get_sid,get_rac_state,create_dir
from connection.ssh_input import ssh_input_noprint,ssh_ftp,ssh_trans_time

# 清理数据库日志
@log
def ora_drop_tables(os_args,drop_tables_dict):
    print('''
************************************************************
本脚本用于生成用户下批量快速删除表对象的脚本
本脚本适用于单个用户下具有几万表对象的场景

## 支持的操作系统和数据库版本配对
操作系统：LINUX/AIX/UNIX
数据库版本：Oracle 10g-19c
源数据库架构：单机
************************************************************''')
    sid = drop_tables_dict['sid']
    script_dir = drop_tables_dict['script_dir']
    drop_user = drop_tables_dict['drop_user']
    drop_user_passwd = drop_tables_dict['drop_user_passwd']
    oracle_home = drop_tables_dict['oracle_home']
    gap = drop_tables_dict['gap']
    script_path = f'{script_dir}/ora_drop_tables.sh'.replace('//','/')
    ssh_ftp(os_args,script_path,'ora_drop_tables\get_drop_table.sh','put')
    ssh_input_noprint(os_args,f'chmod 775 {script_path}')

    run_res = ssh_input_noprint(os_args,f'{script_path} {sid} {script_dir} {drop_user} {drop_user_passwd} {oracle_home} {gap}' )
    print(''.join(run_res))

    print(f'\nINFO:生成truncate 用户{drop_user} 下表脚本路径为:\n{script_dir}/parall_cmd_truncate.sh')
    print(f'\nINFO:生成drop 用户{drop_user} 下表脚本路径为:\n{script_dir}/parall_cmd_drop.sh\n')
    ssh_input_noprint(os_args,f'rm -f {script_path}')



    return run_res