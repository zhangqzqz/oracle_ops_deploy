# -*- coding:utf-8 -*-

import sys
from ora_expdp.ora_expdp_method import  check_expdp,get_init_tbs_sql,check_profile
from method import parse_conn,log,check_db,log,get_sid,get_rac_state,create_dir
from connection.ssh_input import ssh_input_noprint,ssh_scp


# do something of expdp:
@log
def expdp(db_args,sync_obj,sys_user,sys_passwd,mode,ssh_port,degree,path,dbf_path,target_os_args,tag_dmp_path):

    ip =db_args[0]
    os_args = [ip,ssh_port,sys_user,sys_passwd]
    check_db(db_args,mode)
    
    create_dir_res = create_dir(db_args,mode,os_args,path)
    if create_dir_res == 'create dir s':
        expdp_cmd,impdp_cmd,deflt_info = check_expdp(mode,sync_obj,sys_user,sys_passwd,db_args,ssh_port,degree,path,dbf_path)
        if expdp_cmd != 1 and expdp_cmd != 'no' and expdp_cmd != 'none user':
            print(f"\nINFO：expdp命令运行中，请关注本地ora_ops.log或数据库环境下的导出日志")
            expdp_res = ssh_input_noprint(os_args,expdp_cmd)
            print(''.join(expdp_res))
            if 'completed' in ''.join(expdp_res):
                dmp_file_name = path+'/'+expdp_cmd.split('dumpfile=')[-1].split(' ')[0]
                print(f"\nINFO:expdp命令执行完成,导出文件路径为：{dmp_file_name}。")
                print("\nINFO:开始传输导出文件到目标库")
                tag_dmp_file_path = tag_dmp_path+'/'+expdp_cmd.split('dumpfile=')[-1].split(' ')[0]
                ssh_scp(os_args,target_os_args,dmp_file_name,tag_dmp_file_path)
                print(f"\nINFO:导出文件传输完成,目标环境路径为{tag_dmp_file_path}")
                get_init_tbs_sql(db_args,deflt_info,mode,dbf_path)
                profile_list = list(set([i[3] for i in deflt_info]))
                check_profile(db_args,mode,profile_list)
                tag_create_sql = f"create or replace directory mc_dump_dir as '{tag_dmp_path}';\ngrant read,write on directory mc_dump_dir to public;"
                print(f"\nINFO:目标库导入路径目录创建语句为：\n{tag_create_sql}")
                print(f"\nINFO:目标库导入命令为：\n###\n{impdp_cmd}\n###")
                return "expdp s"
            else:
                print("\nWARNING:expdp命令执行失败。")
                return "expdp f"
        else:
            return 1

    else:
        print("\nERRO:数据库目录创建失败，详情请看日志。")
        return create_dir_res
