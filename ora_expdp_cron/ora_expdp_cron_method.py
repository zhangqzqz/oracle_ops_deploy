# -*- coding:utf-8 -*-
import functools
import re
import time
import logging

from prettytable import PrettyTable,ALL
from method import log,res_table,check_db,get_sid,get_rac_state
from connection.ora_conn import ora_all,ora_no_fetch,ora_func,ora_no_fetch_more
from connection.ssh_input import ssh_input_noprint

# logging
logging.basicConfig(format="%(levelname)s\t%(asctime)s\t%(message)s",filename="ora_expdp.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)







# input the prallel if you want
@log
def input_parallel(os_args,degree):
    if degree == 0:
        degree = 1
    else:
        pass
    cpu_cnt = int(ssh_input_noprint(os_args,'''cat /proc/cpuinfo | grep "processor" |wc -l''')[0].replace('\n',''))
    p_tmp = cpu_cnt // 2 + cpu_cnt % 2 
    print(f"\nINFO:导出环境的逻辑CPU数为{cpu_cnt},推荐并行度应不超过{p_tmp},用户选择并行度为{degree}")
    if degree > p_tmp:
        print("WARRNING:请不要选择大于1/2倍逻辑CPU数的并行度！")
        return 'no'
    return degree






# estimate the size of this expdp
@log
def estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd):
    sys_user = os_args[2]
    print("\nINFO:现在开始预估导出文件大小,可能会花费些许时间.")
    if '.' not in sync_obj and sync_obj != 'FULL_EXPDP':
        estimate_size_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp \\"'\\" / as sysdba\\"'\\"  schemas={sync_obj} ESTIMATE_ONLY=y'''
    elif  sync_obj == 'FULL_EXPDP':
        estimate_size_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp \\"'\\" / as sysdba\\"'\\"  full=y ESTIMATE_ONLY=y'''
    else:
        estimate_size_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp \\"'\\" / as sysdba\\"'\\"  tables={sync_obj} ESTIMATE_ONLY=y'''
    ssh_input_noprint(os_args,f"echo '''{estimate_size_cmd}'''>/home/{sys_user}/estimate_size.sh\nchmod +x /home/{sys_user}/estimate_size.sh")
    estimate_size_res = ssh_input_noprint(os_args,f'/home/{sys_user}/estimate_size.sh')

    estimate_size_tmp = [i for i in estimate_size_res if 'Total estimation using BLOCKS method:' in i]

    if estimate_size_tmp != []:
        estimate_size = estimate_size_tmp[0].split(':')[-1].replace('\n','')
    else:
        estimate_size = '\nestimate size error \n'+''.join(estimate_size_res)

    return estimate_size


# clean the data pump jobs table info
@log
def clean_dmp_job_tbs(db_args,mode,sid,os_args):
    sys_user = os_args[2]
    select_info_sql = "select 'drop table ' || owner_name || '.' || job_name || ';' from dba_datapump_jobs where state = 'NOT RUNNING'"
    drop_info_sqls_tmp = [sql[0] for sql in ora_all(db_args,select_info_sql,mode)[0]]
    drop_info_sqls = '\n'.join(drop_info_sqls_tmp)

    if drop_info_sqls != '':
        print("\nINFO:开始清理逻辑泵任务状态表.")
        drop_cmd = f"source ~/.bash_profile\nexport ORACLE_SID={sid}\nsqlplus -s / as sysdba<<EOF\n{drop_info_sqls}\nexit\nEOF"
        ssh_input_noprint(os_args,f"echo '''{drop_cmd}'''>/home/{sys_user}/drop_dmp_tbs.sh\nchmod +x /home/{sys_user}/drop_dmp_tbs.sh")
        drop_res = ''.join(ssh_input_noprint(os_args,f"/home/{sys_user}/drop_dmp_tbs.sh"))
        if 'ORA-' not in drop_res.upper():
            print("\nINFO:清理逻辑泵任务状态表完成.") 
        else:
            print(f"\nINFO:清理逻辑泵任务状态表失败.失败原因为:\n{drop_res}") 
    else:
        drop_res = "do not clean"
    return drop_res


# configure crontab for expdp script
@log
def crontab_config(crontab_date_str,os_args,sid):
    sys_user,sys_passwd = os_args[2:4]
    args_list = crontab_date_str.split(' ')
    if len(args_list) != 5:
        print ("ERROR:crontab 时间配置参数填写错误，请确保用一下格式填写：\n分钟 小时 日 月 周,以一个空格隔开，详情参考crontab设置写法")
        return "str error"
    else:
        mi,hour,day,month,week = args_list
        if month != '*':
            period = 'month'
        elif week != '*':
            period = 'week'
        else:
            period = 'day'
        crontab_str = f"# The backup for instance which sid is {sid},and period is {period.upper()}\n{crontab_date_str}    /home/{sys_user}/expdp_{period}_{sid}.sh>/tmp/expdp_{period}_{sid}.out"
        ssh_input_noprint(os_args,f"crontab -l>/home/{sys_user}/mc_crontab")
        ssh_input_noprint(os_args,f"crontab -l>/home/{sys_user}/mc_crontab_bak")
        ssh_input_noprint(os_args,f"echo '''{crontab_str}''' >>/home/{sys_user}/mc_crontab")
        ssh_input_noprint(os_args,f"crontab /home/{sys_user}/mc_crontab")

        return "crontab setup complete",period
        




        
        



# generate the strings of expdp script
@log
def get_expdp_str(db_args,mode,sync_obj,sys_user,sys_passwd,ssh_port,degree,path):
    sync_obj = sync_obj.upper()
    obj_list = tuple(sync_obj.split(','))
    ip,db_user,db_port,db_pwd,db_sid = db_args
    os_args = [ip,ssh_port,sys_user,sys_passwd]
    sid = get_sid(db_args,mode)
    
    # clean dmp jobs table
    drop_res = clean_dmp_job_tbs(db_args,mode,sid,os_args)
    if 'ORA-' in drop_res.upper():
        print("INFO:请自行清理逻辑泵任务表,sql见输出信息")
    
    # schemas expdp
    if '.' not in sync_obj and sync_obj != 'FULL_EXPDP':
        check_obj_sql = f"select SEGMENT_NAME  from dba_segments where owner in {obj_list} "
        check_obj_sql = check_obj_sql.replace(',)',')')
        check_obj,_ = ora_all(db_args,check_obj_sql,mode)
        
        if check_obj[0][0] == None:
            print(f"WARRING:用户 {sync_obj} 不存在!请检查你要导出的对象是否正确.")
            return 1
        estimate_size = estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd)
        if 'estimate size error' not in estimate_size :
            print(f"\nINFO:导出对象预估大小：{estimate_size}.")
            if 'T' in estimate_size:
                print("\nINFO:导出对象过大,请确认是否需要使用逻辑泵导出备份!")
                return 1
        else:
            print(f"ERROR:导出预估脚本执行失败,报错为:{estimate_size}")
            return 1
        parallel = input_parallel(os_args,degree)
        
        if parallel == 'no':
            return 'no'
        elif parallel == 1:
            expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"  schemas={sync_obj} directory=mc_dump_dir dumpfile=\$FILE_TARGET.dmp logfile=\$FILE_LOG'''
        else:
            rac = get_rac_state(db_args,mode)
            if rac == 'TRUE':
                expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"  schemas={sync_obj} directory=mc_dump_dir parallel={parallel}  cluster=n dumpfile=\${{FILE_TARGET}}_%U.dmp logfile=\$FILE_LOG'''
            else:
                expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"  schemas={sync_obj} directory=mc_dump_dir parallel={parallel} dumpfile=\${{FILE_TARGET}}_%U.dmp logfile=\$FILE_LOG'''
    # full db expdp
    elif sync_obj == 'FULL_EXPDP':
        estimate_size = estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd)
        if 'estimate size error' not in estimate_size :
            print(f"\nINFO:导出对象预估大小：{estimate_size}.")
            if 'T' in estimate_size:
                print("\nINFO:导出对象过大,请确认是否需要使用逻辑泵导出备份!")
                return 1
        else:
            print(f"ERROR:导出预估脚本执行失败,报错为:{estimate_size}")
            return 1
        parallel = input_parallel(os_args,degree)
        if parallel == 'no':
            return 'no'
        elif parallel == 1:
            expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"   directory=mc_dump_dir dumpfile=\$FILE_TARGET.dmp logfile=\$FILE_LOG full=y'''
            
        else:
            rac = get_rac_state(db_args,mode)
            if rac == 'TRUE':
                expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"   directory=mc_dump_dir cluster=n parallel={parallel} dumpfile=\${{FILE_TARGET}}_%U.dmp logfile=\$FILE_LOG full=y'''

            else:
                expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"   directory=mc_dump_dir parallel={parallel} dumpfile=\${{FILE_TARGET}}_%U.dmp logfile=\$FILE_LOG full=y'''
        
    # tables expdp
    else:
  
        for obj in obj_list:
            owner,table = obj.split('.')
            check_obj_sql = f"select segment_name  from dba_segments where owner = '{owner}' and segment_name = '{table}'" 
            check_obj,_ = ora_all(db_args,check_obj_sql,mode)
            if check_obj[0][0] == None:
                print(f"WARRING:表 {owner}.{table} 不存在!请检查你要导出的对象是否正确.")
                return 1
        estimate_size = estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd)
        if 'estimate size error' not in estimate_size :
            print(f"\nINFO:导出对象预估大小：{estimate_size}.")
            if 'T' in estimate_size:
                print("\nINFO:导出对象过大,请确认是否需要使用逻辑泵导出备份!")
                return 1
        else:
            print(f"ERROR:导出预估脚本执行失败,报错为:{estimate_size}")
            return 1
        parallel = input_parallel(os_args,degree) 
        if parallel == 'no':
            return 'no'
        elif parallel == 1:
            expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"   tables={sync_obj} directory=mc_dump_dir dumpfile=\$FILE_TARGET.dmp logfile=\$FILE_LOG'''
        
        else:
            rac = get_rac_state(db_args,mode)
            if rac == 'TRUE':
                expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"   tables={sync_obj} directory=mc_dump_dir cluster=n parallel={parallel } dumpfile=\${{FILE_TARGET}}_%U.dmp logfile=\$FILE_LOG '''
       
            else:
                expdp_cmd = f'''expdp \\"'\\" / as sysdba\\"'\\"   tables={sync_obj} directory=mc_dump_dir parallel={parallel } dumpfile=\${{FILE_TARGET}}_%U.dmp logfile=\$FILE_LOG '''

    return expdp_cmd







