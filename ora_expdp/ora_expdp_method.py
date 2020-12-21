# -*- coding:utf-8 -*-
import functools
import re
import time
import logging

from prettytable import PrettyTable,ALL
from method import log,res_table,check_db,get_sid,get_rac_state
from connection.ora_conn import ora_all,ora_no_fetch,ora_func
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

# get the schemas's DEFAULT_TABLESPACE and DEFAULT_TEMP
@log
def default_info(sync_obj,db_args,mode):
    sync_obj = sync_obj.upper()
    if sync_obj == "FULL_EXPDP":
        select_deflt_info_sql = '''select distinct b.username,a.tablespace_name,b.TEMPORARY_TABLESPACE,b.profile from dba_tablespaces a, dba_users b,dba_segments c \
    where a.tablespace_name not in ('SYSTEM','SYSAUX') and a.contents = 'PERMANENT'  \
        and a.tablespace_name=c.tablespace_name and b.username=c.owner \
            group by b.username,a.tablespace_name,b.TEMPORARY_TABLESPACE,b.profile
'''
    else:
        schemas = "','".join(list(set([i.split('.')[0] for i in sync_obj.split(',')])))
        select_deflt_info_sql = f'''select distinct b.username,a.tablespace_name,b.TEMPORARY_TABLESPACE,b.profile from dba_tablespaces a, dba_users b,dba_segments c \
    where a.tablespace_name not in ('SYSTEM','SYSAUX') and a.contents = 'PERMANENT'  \
        and a.tablespace_name=c.tablespace_name and b.username=c.owner and username in  ('{schemas}')\
            group by b.username,a.tablespace_name,b.TEMPORARY_TABLESPACE,b.profile
'''
    deflt_info,title = ora_all(db_args,select_deflt_info_sql,mode)
    if deflt_info !=[]:
        info_table = res_table(deflt_info,title)
        print("\nINFO:导出对象用户的策略、默认表空间及默认临时表空间信息如下：")
        print(info_table)
    else:
        pass
    return deflt_info

# generate some sql for init tbs
@log 
def get_init_tbs_sql(db_args,deflt_info,mode,dbf_path):
    tbs_list = list(set([i[1] for i in deflt_info]))
    temp_tbs_list = list(set([i[2] for i in deflt_info]))

    init_tbs_sql_list = []
    init_temp_sql_list = []
    dbf_dir = dbf_path
    for tbs_name in tbs_list:
        select_dbf_cnt_sql = f"SELECT count(*)  from dba_data_files where  tablespace_name='{tbs_name}'"
        datafile_cnt,_ = ora_all(db_args,select_dbf_cnt_sql,mode)
        create_tbs_sql = f"create tablespace {tbs_name} datafile '{dbf_dir}/{tbs_name}01.dbf' size 10m autoextend on;".replace('//','/')
        init_tbs_sql_list.append(create_tbs_sql)
        for dbf_id in range(2,datafile_cnt[0][0]+1):
            add_db_file_sql = f"alter tablespace {tbs_name} add datafile '{dbf_dir}/{tbs_name}{dbf_id}.dbf' size 10m autoextend on;".replace('//','/')
            init_tbs_sql_list.append(add_db_file_sql)
    for temp_tbs_name in temp_tbs_list:
        create_temp_tbs_sql = f"create temporary tablespace {tbs_name} tempfile '{dbf_dir}/{temp_tbs_name}01.dbf' size 10m autoextend on;".replace('//','/')
        init_temp_sql_list.append(create_temp_tbs_sql)
    print("\nINFO:根据导出数据库环境生成的数据表空间初始化语句如下：\n###")
    print('\n'.join(init_tbs_sql_list))
    print("###")
    print("\nINFO:根据导出数据库环境生成的默认临时表空间初始化语句如下：\n###")
    print('\n'.join(init_temp_sql_list))
    print("###")
    print("\nINFO:请根据实际情况在目标环境运行初始化表空间的语句.")
    return init_tbs_sql_list,init_temp_sql_list


# estimate the size of this expdp
@log
def estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd):
    print("\nINFO:现在开始预估导出文件大小,可能会花费些许时间.")
    if '.' not in sync_obj and sync_obj != 'FULL_EXPDP':
        estimate_size_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}  schemas={sync_obj} ESTIMATE_ONLY=y'''
    elif  sync_obj == 'FULL_EXPDP':
        estimate_size_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}  full=y ESTIMATE_ONLY=y'''
    else:
        estimate_size_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}  tables={sync_obj} ESTIMATE_ONLY=y'''
    estimate_size_res = ssh_input_noprint(os_args,estimate_size_cmd)
    estimate_size_tmp = [i for i in estimate_size_res if 'Total estimation using BLOCKS method:' in i][0]
    estimate_size = estimate_size_tmp.split(':')[-1].replace('\n','')
    return estimate_size


# check the profile for users and get the ddl sql
@log
def check_profile(db_args,mode,profile_list):
    profile_list = [i for i in profile_list if i !='DEFAULT' and i!='MONITORING_PROFILE']

    if profile_list == []:
        print("\nINFO:目标数据库无需添加新的用户profile策略.")
        return profile_list
    else:
        func_name = 'PROFILE'
        ddl_list = []
        for profile in profile_list:
            profile_ddl_res = ora_func(db_args,func_name,profile,mode)
            ddl_list.append(profile_ddl_res)
        print("\nINFO:根据导出数据库环境生成的用户profile策略ddl语句如下：\n###")
        print('\n'.join(ddl_list))
        return profile_ddl_res


# precheck before expdp and generate the expdp and cmd
@log
def check_expdp(mode,sync_obj,sys_user,sys_passwd,db_args,ssh_port,degree,path,dbf_path):
    sync_obj = sync_obj.upper()
    obj_list = tuple(sync_obj.split(','))

    ip,db_user,db_port,db_pwd,db_sid = db_args
    os_args = [ip,ssh_port,sys_user,sys_passwd]
    sid = get_sid(db_args,mode)
    
    mytime=time.strftime("%Y%m%d%H%M", time.localtime())
    deflt_info = default_info(sync_obj,db_args,mode)
    if deflt_info ==[]:
        print("\nERROR:数据库用户不存在,请检查后重新输入!")
        return "none user"

    # schemas expdp
    if '.' not in sync_obj and sync_obj != 'FULL_EXPDP':
        check_obj_sql = f"select SEGMENT_NAME  from dba_segments where owner in {obj_list} "
        check_obj_sql = check_obj_sql.replace(',)',')')
        check_obj,_ = ora_all(db_args,check_obj_sql,mode)
        
        if check_obj== []:
            print(f"WARRING:用户 {sync_obj} 不存在!请检查你要导出的对象是否正确.")
            return 1
        estimate_size = estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd)
        print(f"\nINFO:导出对象预估大小：{estimate_size}.")
        parallel = input_parallel(os_args,degree)
        if parallel == 'no':
            return 'no'
        elif parallel == 1:
            expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}  schemas={sync_obj} directory=mc_dump_dir dumpfile=schemas_{mytime}.dmp logfile=schemas_{mytime}.log'''
            impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'" schemas={sync_obj} directory=mc_dump_dir dumpfile=schemas_{mytime}.dmp logfile=impdp_schemas_{mytime}.log'''
        else:
            rac = get_rac_state(db_args,mode)
            if rac == 'TRUE':
                expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}  schemas={sync_obj} directory=mc_dump_dir parallel={parallel}  cluster=n dumpfile=schemas_{mytime}_%U.dmp logfile=schemas_{mytime}.log'''
                impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'" schemas={sync_obj} directory=mc_dump_dir parallel={parallel} cluster=n  dumpfile=schemas_{mytime}_%U.dmp logfile=impdp_schemas_{mytime}.log'''

            else:
                expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}  schemas={sync_obj} directory=mc_dump_dir parallel={parallel} dumpfile=schemas_{mytime}_%U.dmp logfile=schemas_{mytime}.log'''
                impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'" schemas={sync_obj} directory=mc_dump_dir parallel={parallel}   dumpfile=schemas_{mytime}_%U.dmp logfile=impdp_schemas_{mytime}.log'''
    # full db expdp
    elif sync_obj == 'FULL_EXPDP':
        estimate_size = estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd)
        print(f"\nINFO:导出对象预估大小：{estimate_size}.")
        parallel = input_parallel(os_args,degree)
        if parallel == 'no':
            return 'no'
        elif parallel == 1:
            expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}   directory=mc_dump_dir dumpfile=full_{mytime}.dmp logfile=full_{mytime}.log full=y'''
            impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'"  directory=mc_dump_dir dumpfile=full_{mytime}.dmp logfile=impdp_full_{mytime}.log full=y'''
            
        else:
            rac = get_rac_state(db_args,mode)
            if rac == 'TRUE':
                expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}   directory=mc_dump_dir cluster=n parallel={parallel} dumpfile=full_{mytime}_%U.dmp logfile=full_{mytime}.log full=y'''
                impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'"  directory=mc_dump_dir cluster=n parallel={parallel} dumpfile=full_{mytime}_%U.dmp logfile=impdp_full_{mytime}.log full=y'''

            else:
                expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}   directory=mc_dump_dir parallel={parallel} dumpfile=full_{mytime}_%U.dmp logfile=full_{mytime}.log full=y'''
                impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'"  directory=mc_dump_dir parallel={parallel} dumpfile=full_{mytime}_%U.dmp logfile=impdp_full_{mytime}.log full=y'''
        
    # tables expdp
    else:
  
        for obj in obj_list:
            owner,table = obj.split('.')
            check_obj_sql = f"select segment_name  from dba_segments where owner = '{owner}' and segment_name = '{table}'" 
            check_obj,_ = ora_all(db_args,check_obj_sql,mode)
            if check_obj==[]:
                print(f"WARRING:表 {owner}.{table} 不存在!请检查你要导出的对象是否正确.")
                return 1
        estimate_size = estimate_size_expdp(sync_obj,os_args,sid,db_user,db_pwd)
        print(f"\nINFO:导出对象预估大小：{estimate_size}.")
        parallel = input_parallel(os_args,degree) 
        if parallel == 'no':
            return 'no'
        elif parallel == 1:
            expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}   tables={sync_obj} directory=mc_dump_dir dumpfile=tables_{mytime}.dmp logfile=tables_{mytime}.log '''
            impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'"  tables={sync_obj} directory=mc_dump_dir dumpfile=tables_{mytime}.dmp logfile=impdp_tables_{mytime}.log '''
        
        else:
            rac = get_rac_state(db_args,mode)
            if rac == 'TRUE':
                expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}   tables={sync_obj} directory=mc_dump_dir cluster=n parallel={parallel } dumpfile=tables_{mytime}_%U.dmp logfile=tables_{mytime}.log '''
                impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'"  tables={sync_obj} directory=mc_dump_dir cluster=n   parallel={parallel } dumpfile=tables_{mytime}_%U.dmp logfile=impdp_tables_{mytime}.log '''
       
            else:
                expdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID={sid}\nexpdp {db_user}/{db_pwd}   tables={sync_obj} directory=mc_dump_dir parallel={parallel } dumpfile=tables_{mytime}_%U.dmp logfile=tables_{mytime}.log '''
                impdp_cmd = f'''source ~/.bash_profile\nexport ORACLE_SID=<SID>\nimpdp "'" / as sysdba "'"  tables={sync_obj} directory=mc_dump_dir parallel={parallel } dumpfile=tables_{mytime}_%U.dmp logfile=impdp_tables_{mytime}.log '''

    
    
    print(f"\nINFO:导出命令为：\n###\n{expdp_cmd}\n###")
    
    return expdp_cmd,impdp_cmd,deflt_info







