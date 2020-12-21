
oracle 自动化运维工具

修订记录

| 作者 | 版本 | 时间       | 备注       |
| ---- | ---- | ---------- | ---------- |
| 张全针 | v1.0 | 2020/04/17 | 逻辑泵备份功能          |


## 定位
        给MC公司内部人员使用，提供自动化运维功能，提高工作效率


## 先决条件

        1.执行环境与目标环境打通ssh连接
        2.执行环境需存在Oracle客户端client libraries（若已存在oracle环境也可以）

## 支持的操作系统和数据库版本配对
        操作系统支持：rehl5，rehl6，rehl7
        数据库版本支持：Oracle10g单机及RAC,Oracle11g单机及RAC,Oracle 12c-19c CDB单机及rac
        后续待适配：pdb实例




## 使用说明




### python运行环境

python 3


        1. 进入脚本目录
        pip install -r requirements.txt    #安装项目python依赖包cx_Oracle,prettytable与paramiko。  #第一次安装时用

        如果网速慢，可以用以下命令安装，使用国内的PIP源

   ```cx_Oracle
   pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
   ```




## 代码说明

| 文件或目录       | 功能                 | 备注                                                         |
| --------------- | -------------------- | ------------------------------------------------------------ |
| ora_ops.py      | 命令行主入口         |                                                             |
| method.py       | 主要功能和函数方法    |                                                              |
| ora_ops.log   | 安装脚本输出结果日志  |                                                              |

## 主程序的使用
python ora_ops.py

### 命令行参数介绍

          optional arguments:
          -h, --help            show this help message and exit
          -c CONN_STR, --conn_str CONN_STR
                              输入你的数据库连接串：用户名/密码@ip:端口/服务名,请使用system用户登录,以保证有足够的权限
          -m MODE, --mode MODE  数据库连接方式，可填'sysdba'或'default_auth',默认为'default_auth'
          -u USER, --user USER  操作系统oracle用户,默认为'oracle'
          -p PASSWORD, --password PASSWORD
                              操作系统oracle用户密码
          -P SSH_PORT, --ssh_port SSH_PORT
                              操作系统ssh的端口号,默认为22
          -d DEGREE, --degree DEGREE
                              导入导出时的并行度,默认为1，即不开启并行
          -path PATH, --path PATH
                              导入导出文件存放路径
          -s SYNC_OBJ, --sync_obj SYNC_OBJ
                              想要导出的对象，例如，全库：full_expdp | 多用户：test,test1 | 多表：test.t1,test.t2,test2.t10
          -ftp_ip FTP_IP, --ftp_ip FTP_IP
                              使用ftp服务时远端服务器的ip地址，默认值为'FTP_IP'
          -ftp_dir FTP_DIR, --ftp_dir FTP_DIR
                              使用ftp时远端服务器的地址,，默认值为'FTP_DIR'
          -ftp_user FTP_USER, --ftp_user FTP_USER
                              使用ftp服务时远端服务器的用户名,，默认值为'FTP_USER'
          -ftp_passwd FTP_PASSWD, --ftp_passwd FTP_PASSWD
                              使用ftp服务时远端服务器的用户密码,默认值为'FTP_PASSWD'
          -retention_day RETENTION_DAY, --retention_day RETENTION_DAY
                              备份本地保留时间天数,默认为5天
          -crontab_date CRONTAB_DATE, --crontab_date CRONTAB_DATE
                              调用crontab时的定时参数设置,一般格式为:<分 时 日 月 周>,详细写法参考crontab写法
          -i {check_instance,expdp,create_dir,check_lock,expdp_crontab}, --item {check_instance,create_dir,expdp_crontab}
                              check_instance:检查数据库|create_dir:创建数据库导入导出目录|expdp_crontab:设置逻辑泵备份任务

### 使用举例

#### 11g单机上设置一个逻辑泵全备任务并将备份发至远端
          python ora_ops.py -c system/oracle@192.168.238.56:1521/zqz -u oracle -p oracle -s full_expdp -i expdp_crontab  -d 2 -path /bak -ftp_ip "192.168.238.35" -ftp_user oracle -ftp_passwd oracle  -ftp_dir /oracle/oradata -crontab_date "1 2 * * *"

          INFO:检查数据库信息 192.168.238.56:1521/zqz:
          +---------+---------------+--------+------------+
          | INST_ID | INSTANCE_NAME | STATUS |  VERSION   |
          +---------+---------------+--------+------------+
          |    1    |      zqz      |  OPEN  | 11.2.0.4.0 |
          +---------+---------------+--------+------------+


          INFO:192.168.238.56:1521/zqz
          数据库目录MC_DUMP_DIR：/bak 创建成功
          +-------+----------------+----------------+
          | OWNER | DIRECTORY_NAME | DIRECTORY_PATH |
          +-------+----------------+----------------+
          |  SYS  |  MC_DUMP_DIR   |      /bak      |
          +-------+----------------+----------------+

          
          INFO:开始清理逻辑泵任务状态表.

          INFO:清理逻辑泵任务状态表完成.
          
          INFO:现在开始预估导出文件大小,可能会花费些许时间.

          INFO:导出对象预估大小： 60.93 MB.

          INFO:导出环境的逻辑CPU数为2,推荐并行度应不超过4,用户选择并行度为2

          INFO:逻辑备份脚本路径为：/home/oracle/expdp_day_zqz.sh

          INFO:当前crontab定时任务内容为:
          * */1 * * * python /tmp/ogg_monitor/ogg_monitor.py >> /tmp/ogg_monitor/ogg_monitor.log
          # The backup for instance which sid is zqz,and period is DAY
          1 2 * * *    /home/oracle/expdp_day_zqz.sh>/tmp/expdp_day_zqz.out

