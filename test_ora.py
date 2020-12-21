import pytest
from ora_expdp.ora_expdp_method import check_expdp,default_info,check_profile
from method import check_db,parse_conn
from connection.ora_conn import ora_no_fetch
from ora_expdp_cron.ora_expdp_cron import expdp_cron

conn_str = "system/oracle@192.168.238.56:1521/zqz"
dmp_dir = "/tmp"
mode = 'default_auth'
sync_obj = 'full_expdp'
sys_user = 'oracle'
sys_passwd = 'oracle'
ssh_port =22
args = parse_conn(conn_str)
profile_list = ['DEFAULT','PROFILE_TEST','PROFILE_TEST1']
degree =2
path = "/bak"
ftp_ip = '192.168.238.35'
ftp_dir = "/oracle/oradata"
ftp_user= "oracle"
ftp_passwd = "oracle"
crontab_date_str = '1 1 * * *'

# def test_crt_dir():
#     assert create_dir(conn_str,dmp_dir,mode)  == 'create dir s'
#check_expdp(conn_str,mode,sync_obj,sys_user,sys_passwd,args)
# res = default_info(sync_obj,conn_str,mode)
# print (res)

# if __name__ == "__main__":
#     pytest.main()

#check_profile(conn_str,mode,profile_list)

expdp_cron(conn_str,sync_obj,sys_user,sys_passwd,mode,ssh_port,degree,path,ftp_ip,ftp_dir,ftp_user,ftp_passwd,crontab_date_str)
