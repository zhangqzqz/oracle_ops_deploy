#!/usr/bin/env python

import sys
from ora_expdp_cron.ora_expdp_cron_method import crontab_config,estimate_size_expdp,get_expdp_str
from method import parse_conn,log,check_db,log,get_sid,get_rac_state,create_dir
from connection.ssh_input import ssh_input_noprint,ssh_ftp,ssh_trans_time

# 清理数据库日志
@log
def ora_clean_log(os_args,retention_day):
    ssh_ftp(os_args,'/tmp/ora_clean.sh','ora_clean_log\del_log.sh','put')
    ssh_input_noprint(os_args,'chmod 775 /tmp/ora_clean.sh')

    run_res = ssh_trans_time(os_args,f'/tmp/ora_clean.sh {retention_day} ')

    ssh_input_noprint(os_args,'rm -f  /tmp/ora_clean.sh')


    return run_res