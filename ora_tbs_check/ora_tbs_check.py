#!/usr/bin/env python

import sys
from ora_expdp_cron.ora_expdp_cron_method import crontab_config,estimate_size_expdp,get_expdp_str
from method import parse_conn,log,check_db,log,get_sid,get_rac_state,create_dir
from connection.ssh_input import ssh_input_noprint,ssh_ftp,ssh_trans_time

# 清理数据库日志
@log
def ora_tbs_check(os_args,sid):
    ssh_ftp(os_args,'/tmp/ora_tbs_check.sh','ora_tbs_check\\add_tbs_check_and_advice.sh','put')
    ssh_input_noprint(os_args,'chmod 775 /tmp/ora_tbs_check.sh')
    print("\nINFO:开始执行脚本：")
    run_res = ssh_trans_time(os_args,f'/tmp/ora_tbs_check.sh {sid} ')

    ssh_input_noprint(os_args,'rm -f  /tmp/ora_tbs_check.sh')


    return run_res