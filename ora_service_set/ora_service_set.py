#!/usr/bin/env python

import sys
from method import parse_conn,log,check_db,log,get_sid,get_rac_state,create_dir
from connection.ssh_input import ssh_input_noprint,ssh_ftp,ssh_trans_time

# 清理数据库日志
@log
def ora_service_set(os_args):
    print('''\nINFO:Oracle自启动关闭使用范围:
1.Oracle数据库单机环境
2.Oracle数据库版本11g以上 
3.主机上存在多个版本的数据库和监听
4.Linux 6-7
    ''')
    print("\nINFO:开始配置脚本:")
    ssh_ftp(os_args,'/tmp/ora_dbservice_set.sh','ora_service_set\DbServiceSet.sh','put')
    ssh_input_noprint(os_args,'chmod 775 /tmp/ora_dbservice_set.sh')
    print('\nINFO: 获取数据库环境服务信息:')
    run_res = ssh_input_noprint(os_args,f'/tmp/ora_dbservice_set.sh')
    print(''.join(run_res))
    ora_home = [res for res in run_res if 'ORACLE_HOME is:' in res ][0].split(' ')[-1]
    db_services = input("请根据已知信息填写要添加的数据库服务,若不添加，请回车：\n")
    listener_services = input("请根据已知信息填写要添加的监听服务,若有多个，请用逗号隔开，若不添加，请回车：\n")
    if db_services != '' and listener_services !='':
        run_cmd = f"/tmp/ora_dbservice_set.sh -d {db_services} -o {ora_home} [-l {listener_services}]"
    elif db_services!='' and listener_services == '':
        run_cmd = f"/tmp/ora_dbservice_set.sh -d {db_services} -o {ora_home}"
    elif db_services == '' and listener_services != '':
        run_cmd = f"/tmp/ora_dbservice_set.sh  -o {ora_home} [-l {listener_services}]"   
    else:
        print("\nWARNING:未知错误！")
        return "err"

    print("\nINFO:开始执行数据库服务添加自启动：") 
    ssh_trans_time(os_args,run_cmd)
    print("\nINFO:检查通过当前脚本设置的自启动资源信息：")
    check_res = ssh_input_noprint(os_args,'/tmp/ora_dbservice_set.sh -m l')
    print(''.join(check_res))




    ssh_input_noprint(os_args,'rm -f  /tmp/ora_dbservice_set.sh')
    print('''\nINFO: 配置完成后，需要通过service DbService stop或者systemctl stop DbService 停止资源一次，进行验证
  支持管理命令如下
Linux7以下：`service DbService start｜stop｜restart`
Linux7以上：`systemctl start｜stop｜status DbService`''')

    return check_res