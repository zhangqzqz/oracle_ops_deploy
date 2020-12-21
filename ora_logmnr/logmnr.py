# -*- coding:utf-8 -*-

'''
the tool for oracle logmnr
'''
import logging
import time
from connection.ora_conn import ora_all,ora_func,ora_proc_use,ora_no_fetch,ora_no_fetch_more
from method import check_instance,res_table,log
from ora_logmnr.logmnr_const import SQL_LOG_MNR




# 检查归档是否开启
@log
def check_archivelog_status(db_args,mode):
    print("\nINFO:开始检查数据库归档是否开启:")
    GET_ARCHIVELOG_STATUS_SQL = SQL_LOG_MNR['GET_ARCHIVELOG_STATUS_SQL']
    status_res = ora_all(db_args,GET_ARCHIVELOG_STATUS_SQL,mode)[0][0][0]
    if status_res.upper() == 'ARCHIVELOG':
        print("\nINFO:数据库归档已经开启!")
        return 'arch'
    elif status_res.upper() == 'NOARCHIVELOG':
        print("\nINFO:数据库归档未开启!,无法进行日志挖掘!")
        return 'unarch'
    else:
        print("\nWARNING:查询失败！请检查数据库是否正常！")
        return 'ora_err'


# 检查附加日志是否开启
@log
def check_supplelog_status(db_args,mode):
    print("\nINFO:开始检查数据库附加日志是否开启:")
    GET_SUPPERLOG_STATUS_SQL = SQL_LOG_MNR['GET_SUPPERLOG_STATUS_SQL']
    status_res = ora_all(db_args,GET_SUPPERLOG_STATUS_SQL,mode)[0][0][0]
    if status_res.upper() == 'YES':
        print("\nINFO:数据库最小附加日志已打开!")
        return 'yes'
    elif status_res.upper() == 'NO':
        print("\nINFO:数据库最小附加日志未打开!")
        return 'no'
    else:
        print("\nWARNING:查询失败！请检查数据库是否正常！")
        return 'ora_err'

# 查询挖掘的归档信息
@log
def check_archivelog_info(db_args,mode,start_time,end_time):
    # 查询需要挖掘的归档
    print("\nINFO:开始查询指定时间内的归档信息:")
    GET_ARCHIVELOG_SQL = SQL_LOG_MNR['GET_ARCHIVELOG_SQL']%(start_time,end_time)
    archivedlog_list,_ =  ora_all(db_args,GET_ARCHIVELOG_SQL,mode)
    
    if archivedlog_list == []:
        print("\nINFO:给定时间内，没有发现任何归档!")
        return 'null arch'
    else:
        print(f"\nINFO:指定时间 {start_time} -- {end_time} 存在归档,\n归档日志文件数为:{len(archivedlog_list)} 个!")
        # 查询指定的归档归档量
        GET_ARCHIVELOG_SIZE_SQL = SQL_LOG_MNR['GET_ARCHIVELOG_SIZE_SQL'] % (start_time,end_time)
        archivelog_size = ora_all(db_args,GET_ARCHIVELOG_SIZE_SQL,mode)[0][0][0]
        if archivelog_size >20:
            print(f"\nINFO:需要挖掘的归档量为{archivelog_size} G，超过20G，日志量过大，建议缩小时间段!")
            start_time_tmp = input("请重新输入查询起始时间，格式:yyyy-mm-dd hh:MM:ss\n")
            end_time_tmp = input("请重新输入查询结束时间，格式:yyyy-mm-dd hh:MM:ss\n")
            check_archivelog_info(db_args,mode,start_time_tmp,end_time_tmp)
        else:
            print(f"\nINFO:需要挖掘的归档量为{archivelog_size}G")

        return archivedlog_list,archivelog_size
        

# 挖掘归档日志
@log
def logmnr_run_archlog(db_args,archivedlog_list,mode,start_time,end_time):
    print("\nINFO:开始归档日志文件挖掘:")
    
    start_run_time = time.strftime("%Y%m%d%H%M", time.localtime())
    LOGMNR_NEW_LOGFILE_SQL = SQL_LOG_MNR['LOGMNR_NEW_LOGFILE_SQL']
    LOGMNR_ADD_LOGFILE_SQL = SQL_LOG_MNR['LOGMNR_ADD_LOGFILE_SQL']
    LOGMNR_START_SQL = SQL_LOG_MNR['LOGMNR_START_SQL']
    CREATE_LOGMNR_TABLE_SQL = SQL_LOG_MNR['CREATE_LOGMNR_TABLE_SQL'] % (start_run_time)
    LOGMNR_END_SQL = SQL_LOG_MNR['LOGMNR_END_SQL']
    
    mc_logmnr_tb_name = CREATE_LOGMNR_TABLE_SQL.split(' ')[6]
    new_logfile_sql = LOGMNR_NEW_LOGFILE_SQL % (archivedlog_list[0])
    add_logfile_sql = ''.join([LOGMNR_ADD_LOGFILE_SQL%(i) for i in archivedlog_list[1:]])

    run_logmnr_sql = new_logfile_sql + add_logfile_sql + LOGMNR_START_SQL +'\n    end;'


    res = ''.join(ora_no_fetch_more(db_args,[run_logmnr_sql,CREATE_LOGMNR_TABLE_SQL,LOGMNR_END_SQL],mode))
 
    if 'ORA-' in res:
        print("\nWARNING:归档日志挖掘失败，请检查日志!")
        return 'logmnr error'
    else:
        print(f"\nINFO:时间段{start_time} 至 {end_time} 归档日志挖掘成功,已生成记录表为： <{db_args[1]}.mc_logmnr_{start_run_time}>".upper())
        return mc_logmnr_tb_name



# 获取指定表挖掘信息
@log
def get_table_info(db_args,start_time,end_time,table_name,table_owner,mc_logmnr_tb_name,mode):
    print(f"\nINFO:获取表{table_owner}.{table_name} 在{start_time} 至 {end_time} 的历史信息如下：")

    GET_LOGMNR_RES_SQL = SQL_LOG_MNR['GET_LOGMNR_RES_SQL'] % (mc_logmnr_tb_name,table_name,table_owner)
    

    res_get,title = ora_all(db_args,GET_LOGMNR_RES_SQL,mode)
    if res_get !=[]:

        info_table = res_table(res_get,title)
        print(info_table)
    else:
        print(f"\nINFO:表{table_owner}.{table_name} 在{start_time} 至 {end_time} 没有查询到历史数据信息,请确认时间段！")
    

    print(f"\nINFO:如果需要删除本次挖掘信息，请手工执行<drop table {db_args[1]}.{mc_logmnr_tb_name};>")


    



# logmnr日志挖掘主函数
@log
def logmnr_run(db_args,mode,logmnr_dict):
    print('''
************************************************************
本工具适用于Oracle **本地日志挖掘**，当出现误删除表数据或者其它原因时，想追溯历史信息的时候，可以通过本工具进行日志挖掘。

**建议：在业务量小的时候进行，时间跨度不超过5小时。**

工具适用数据库版本：
系统版本：linux
数据库版本：10G 至 19C
************************************************************''')
    start_time = logmnr_dict['start_time']
    end_time = logmnr_dict['end_time']
    table_owner = logmnr_dict['table_owner'].upper()
    table_name = logmnr_dict['table_name'].upper()
    arch_state_res = check_archivelog_status(db_args,mode)
    if arch_state_res == 'arch':
        spl_state_res = check_supplelog_status(db_args,mode)
        if spl_state_res == 'yes':
            archivedlog_list,_ = check_archivelog_info(db_args,mode,start_time,end_time)
            mc_logmnr_tb_name = logmnr_run_archlog(db_args,archivedlog_list,mode,start_time,end_time)
            if mc_logmnr_tb_name != 'logmnr error':
                get_table_info(db_args,start_time,end_time,table_name,table_owner,mc_logmnr_tb_name,mode)
            else:
                return mc_logmnr_tb_name
        else:
            return spl_state_res
    else:
        return arch_state_res