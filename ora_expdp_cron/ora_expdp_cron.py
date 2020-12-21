# -*- coding:utf-8 -*-

import sys
from ora_expdp_cron.ora_expdp_cron_method import crontab_config,estimate_size_expdp,get_expdp_str
from method import parse_conn,log,check_db,log,get_sid,get_rac_state,create_dir
from connection.ssh_input import ssh_input_noprint




# do something of expdp:
@log
def expdp_cron(db_args,sync_obj,sys_user,sys_passwd,mode,ssh_port,degree,path,ftp_ip,ftp_dir,ftp_user,ftp_passwd,crontab_date_str,retention_day):
    ip,db_user,db_port,db_pwd,sid = db_args
    os_args = [ip,ssh_port,sys_user,sys_passwd]
    check_db(db_args,mode)
    backup_dir = path
    create_dir_res = create_dir(db_args,mode,os_args,path)
    if create_dir_res == 'create dir s':
        expdp_str = get_expdp_str(db_args,mode,sync_obj,sys_user,sys_passwd,ssh_port,degree,path)
        crontab_res,period = crontab_config(crontab_date_str, os_args, sid)
        if crontab_res == 'crontab setup complete':

            if expdp_str != 1 and expdp_str != 'no':
                expdp_cron_str = f'''
source ~/.bash_profile
export ORACLE_SID={sid}
BACKUP_HOME={backup_dir}
DAY=\` date +%Y%m%d_%H_%M_%S \`

FILE_TARGET={sid}_{period}_\$DAY
FILE_LOG={sid}_{period}_\$DAY.log

FTP_IP={ftp_ip}
FTP_BACKUP_HOME={ftp_dir}
FTP_USER={ftp_user} 
FTP_PASSWD={ftp_passwd}


export FILE_TARGET
export FILE_LOG
echo "Begin backup database by expdp at Time:"\`date\`

{expdp_str}

echo "Export mission over at Time:"\`date\`
echo "Delete {retention_day} days ago Export File"

find \$BACKUP_HOME -name "{sid}_{period}_*.dmp" -mtime +{retention_day} -exec rm {{}} \;
find \$BACKUP_HOME -name "{sid}_{period}_*.log" -mtime +{retention_day} -exec rm {{}} \;

echo "ALL WORKS COMPLETE! GOOD LUCK!"
echo ---end---;
ftp -n<<!
open \$FTP_IP
user \$FTP_USER \$FTP_PASSWD
lcd \$BACKUP_HOME
cd \$FTP_BACKUP_HOME
prompt
binary
mput *.dmp
cd \$FTP_BACKUP_HOME
mput *.log
close
bye
!
'''
                ssh_input_noprint(os_args,f'''echo "{expdp_cron_str}">/home/{sys_user}/expdp_{period}_{sid}.sh\nchmod +x /home/{sys_user}/expdp_{period}_{sid}.sh''')
                print(f"\nINFO:逻辑备份脚本路径为：/home/{sys_user}/expdp_{period}_{sid}.sh")
                crontab_str_after = ''.join(ssh_input_noprint(os_args,"crontab -l"))
                print(f"\nINFO:当前crontab定时任务内容为:\n{crontab_str_after}")
            else:
                print("\nERROR:备份语句生成失败.")
                ssh_input_noprint(os_args,f"crontab /home/{sys_user}/mc_crontab_bak")
                return expdp_str
        else:
            print("\nERROR:crontab 设置失败.")
            return crontab_res


    else:
        print("\nERRO:数据库目录创建失败，详情请看日志。")
        return create_dir_res
