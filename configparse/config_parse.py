# -*- coding:utf-8 -*-
import os
import configparser




def get_config():
    config = configparser.ConfigParser()
    config.read("config.cfg")

    host = config.get('oracle_db_config','host')
    db_username = config.get('oracle_db_config','db_user')
    db_port = config.getint('oracle_db_config','db_port')
    db_password = config.get('oracle_db_config','db_password')
    db_sid = config.get('oracle_db_config','db_service_name')

    os_username = config.get('oracle_db_config','os_user')
    os_port = config.getint('oracle_db_config','os_port')
    os_password = config.get('oracle_db_config','os_password')



    db_args = [host,db_username,db_port,db_password,db_sid]
    os_args = [host,os_port,os_username,os_password]
    return db_args,os_args


# 获取expdp导出参数
def get_expdp_config():
    config = configparser.ConfigParser()
    config.read("config.cfg")

    degree = config.getint('expdp_config','degree')
    dmp_path = config.get('expdp_config','dmp_path')
    target_dbf_path = config.get('expdp_config','target_dbf_path')
    sync_obj = config.get('expdp_config','sync_obj')
    tag_dmp_path = config.get('expdp_config','target_dmp_path')

    target_ip = config.get('expdp_config','target_ip')
    tag_os_username = config.get('expdp_config','target_os_user')
    tag_os_port = config.getint('expdp_config','target_os_port')
    tag_os_password = config.get('expdp_config','target_os_password')




    return [degree,dmp_path,target_dbf_path,sync_obj,tag_dmp_path],[target_ip,tag_os_port,tag_os_username,tag_os_password]


# 获取expdp crontab导出参数
def get_expdp_cron_config():
    config = configparser.ConfigParser()
    config.read("config.cfg")

    degree = config.getint('expdp_cron_config','degree')
    dmp_path = config.get('expdp_cron_config','dmp_path')

    ftp_ip = config.get('expdp_cron_config','ftp_ip')
    ftp_dir = config.get('expdp_cron_config','ftp_dir')
    ftp_user = config.get('expdp_cron_config','ftp_user')

    ftp_passwd = config.get('expdp_cron_config','ftp_passwd')
    crontab_date_str = config.get('expdp_cron_config','crontab_date_str')
    retention_day = config.get('expdp_cron_config','retention_day')
    sync_obj = config.get('expdp_cron_config','sync_obj')



    return [degree,dmp_path,ftp_ip,ftp_dir,ftp_user,ftp_passwd,crontab_date_str,retention_day,sync_obj]

# 获取指定项目的所有参数
def get_section_config(section):
    config = configparser.ConfigParser()
    config.read("config.cfg")

    secs = config.items(section)
    return (dict(secs))
