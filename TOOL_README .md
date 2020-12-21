
oracle 自动化运维工具

修订记录

| 作者 | 版本 | 时间       | 备注       |
| ---- | ---- | ---------- | ---------- |
| 张全针 | v1.0 | 2020/03/19 | 逻辑泵导出导入功能          |
| 张全针 | v1.1 | 2020/03/23 | 修改交互为命令行参数|
| 张全针 | v2.0 | 2020/04/03 | 添加锁处理功能|
| 张全针 | v2.1 | 2020/04/08 | 优化修复逻辑泵功能|
| 张全针 | v3.0 | 2020/04/17 | 添加逻辑泵备份任务部署功能|
| 张全针 | v3.1 | 2020/06/11 | 添加逻辑泵文件传输等功能|
| 张全针 | v4.1 | 2020/07/07 | 添加日志挖掘功能|
| 张全针 | v5.0 | 2020/07/16 | 添加表空间检查及数据库服务自启动|
| 张全针 | v6.0 | 2020/08/04 | 添加生成批量删表脚本|
| 张全针 | v6.1 | 2020/08/22 | 修复logmnr一个bug|




## 定位
        给MC公司内部人员使用，提供自动化运维功能，提高工作效率


## 先决条件

        1.执行环境与目标环境打通ssh连接
        2.执行环境需存在Oracle客户端client libraries（若已存在oracle环境也可以）

## 支持的操作系统和数据库版本配对
        操作系统支持：rehl5，rehl6，rehl7
        数据库版本支持：Oracle10g单机及RAC,Oracle11g单机及RAC,Oracle 12c-19c noCDB单机及rac
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

### 参数配置文件的使用

     [oracle_db_config]                                     --必备参数,系统参数默认应填写oracle用户参数，在使用clean_log功能时使用root用户
     host=192.168.238.56
     db_user=zqz
     db_port=1521
     db_password=zqz
     db_sid=orcl
     os_port=22
     os_user=oracle
     os_password=oracle



     [expdp_config]                                         --逻辑泵导出功能参数
     degree=1
     dmp_path=/tmp
     target_dbf_path=<DATAFILE_DIR>
     sync_obj=zqz.zqz1,zmy.test                             --想要导出的对象，例如，全库：full_expdp | 多用户：test,test1 | 多表：test.t1,test.t2,test2.t10
     target_ip=192.168.238.56
     target_os_user=oracle
     target_os_password=oracle
     target_os_port=22
     target_dmp_path=/tmp

     [expdp_cron_config]                                    --逻辑泵定时任务功能参数
     degree=1
     dmp_path=/tmp
     ftp_ip=192.168.1.1
     ftp_dir=/tmp
     ftp_user=oracle
     ftp_passwd=oralce
     crontab_date_str=1 1 * * *
     retention_day=5
     sync_obj=zqz.zqz1,zmy.test                             --想要导出的对象，例如，全库：full_expdp | 多用户：test,test1 | 多表：test.t1,test.t2,test2.t10

     [logmnr_config]                                        --日志挖掘功能参数
     start_time = 2020-07-04 17:30:00
     end_time = 2020-07-06 18:30:00
     table_owner = zqz
     table_name = t1



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
     -m MODE, --mode MODE  数据库连接方式，可填'sysdba'或'default_auth',默认为'default_auth'
     -r RETENTION_DAY, --retention_day RETENTION_DAY
                         数据库日志本地保留时间天数
     -i {check_instance,expdp,create_dir,check_lock,expdp_crontab,clean_log}, --item {check_instance,expdp,create_dir,check_lock,expdp_crontab,clean_log}
                         expdp:数据库导出|check_instance:检查数据库|create_dir:创建数据库导入导出目
                         录|expdp_crontab:设置逻辑泵备份任务nce:检查数据库|create_dir:创建数据库导
               入导出目录|expdp_crontab:设置逻辑泵备份任务|logmnr:日志挖掘功能

### 使用举例

#### 1.在11grac环境上导出多用户

     python.exe .\ora_ops.py -i expdp

     
     INFO:检查数据库信息 192.168.238.35:
     +---------+---------------+--------+------------+
     | INST_ID | INSTANCE_NAME | STATUS |  VERSION   |
     +---------+---------------+--------+------------+
     |    1    |    ora11g1    |  OPEN  | 11.2.0.4.0 |
     +---------+---------------+--------+------------+

     INFO:192.168.238.35
     数据库目录MC_DUMP_DIR：/tmp 创建成功
     +-------+----------------+----------------+
     | OWNER | DIRECTORY_NAME | DIRECTORY_PATH |
     +-------+----------------+----------------+
     |  SYS  |  MC_DUMP_DIR   |      /tmp      |
     +-------+----------------+----------------+

     INFO:导出对象用户的策略、默认表空间及默认临时表空间信息如下：
     +----------+-----------------+----------------------+---------+
     | USERNAME | TABLESPACE_NAME | TEMPORARY_TABLESPACE | PROFILE |
     +----------+-----------------+----------------------+---------+
     |   ZQZ    |      USERS      |         TEMP         | DEFAULT |
     +----------+-----------------+----------------------+---------+
     WARRING:表 ZQZ.ASDDSF 不存在!请检查你要导出的对象是否正确.
     PS C:\F_Drive\github\ora_ops> python.exe .\ora_ops.py -i expdp

     INFO:检查数据库信息 192.168.238.35:
     +---------+---------------+--------+------------+
     | INST_ID | INSTANCE_NAME | STATUS |  VERSION   |
     +---------+---------------+--------+------------+
     |    1    |    ora11g1    |  OPEN  | 11.2.0.4.0 |
     +---------+---------------+--------+------------+

     INFO:192.168.238.35
     数据库目录MC_DUMP_DIR：/tmp 创建成功
     +-------+----------------+----------------+
     | OWNER | DIRECTORY_NAME | DIRECTORY_PATH |
     +-------+----------------+----------------+
     |  SYS  |  MC_DUMP_DIR   |      /tmp      |
     +-------+----------------+----------------+

     INFO:导出对象用户的策略、默认表空间及默认临时表空间信息如下：
     +----------+-----------------+----------------------+---------+
     | USERNAME | TABLESPACE_NAME | TEMPORARY_TABLESPACE | PROFILE |
     +----------+-----------------+----------------------+---------+
     |   ZMY    |      USERS      |         TEMP         | DEFAULT |
     +----------+-----------------+----------------------+---------+
     |   ZQZ    |      USERS      |         TEMP         | DEFAULT |
     +----------+-----------------+----------------------+---------+

     INFO:现在开始预估导出文件大小,可能会花费些许时间.

     INFO:导出对象预估大小： 1.187 MB.

     INFO:导出环境的逻辑CPU数为2,推荐并行度应不超过1,用户选择并行度为1

     INFO:导出命令为：
     ###
     source ~/.bash_profile
     export ORACLE_SID=ora11g1
     expdp system/oracle  schemas=ZQZ,ZMY directory=mc_dump_dir dumpfile=schemas_202006111503.dmp logfile=schemas_202006111503.log
     ###

     INFO：expdp命令运行中，请关注本地ora_ops.log或数据库环境下的导出日志

     Export: Release 11.2.0.4.0 - Production on Thu Jun 11 15:04:34 2020

     Copyright (c) 1982, 2011, Oracle and/or its affiliates.  All rights reserved.

     Connected to: Oracle Database 11g Enterprise Edition Release 11.2.0.4.0 - 64bit Production
     With the Partitioning, Real Application Clusters, Automatic Storage Management, OLAP,
     Data Mining and Real Application Testing options
     FLASHBACK automatically enabled to preserve database integrity.
     Starting "SYSTEM"."SYS_EXPORT_SCHEMA_01":  system/******** schemas=ZQZ,ZMY directory=mc_dump_dir dumpfile=schemas_202006111503.dmp logfile=schemas_202006111503.log
     Estimate in progress using BLOCKS method...
     Processing object type SCHEMA_EXPORT/TABLE/TABLE_DATA
     Total estimation using BLOCKS method: 1.187 MB
     Processing object type SCHEMA_EXPORT/USER
     Processing object type SCHEMA_EXPORT/SYSTEM_GRANT
     Processing object type SCHEMA_EXPORT/ROLE_GRANT
     Processing object type SCHEMA_EXPORT/DEFAULT_ROLE
     Processing object type SCHEMA_EXPORT/PRE_SCHEMA/PROCACT_SCHEMA
     Processing object type SCHEMA_EXPORT/SYNONYM/SYNONYM
     Processing object type SCHEMA_EXPORT/TABLE/TABLE
     Processing object type SCHEMA_EXPORT/PACKAGE/PACKAGE_SPEC
     Processing object type SCHEMA_EXPORT/FUNCTION/FUNCTION
     Processing object type SCHEMA_EXPORT/PROCEDURE/PROCEDURE
     Processing object type SCHEMA_EXPORT/PACKAGE/COMPILE_PACKAGE/PACKAGE_SPEC/ALTER_PACKAGE_SPEC
     Processing object type SCHEMA_EXPORT/FUNCTION/ALTER_FUNCTION
     Processing object type SCHEMA_EXPORT/PROCEDURE/ALTER_PROCEDURE
     Processing object type SCHEMA_EXPORT/TABLE/INDEX/INDEX
     Processing object type SCHEMA_EXPORT/TABLE/CONSTRAINT/CONSTRAINT
     Processing object type SCHEMA_EXPORT/TABLE/INDEX/STATISTICS/INDEX_STATISTICS
     Processing object type SCHEMA_EXPORT/VIEW/VIEW
     Processing object type SCHEMA_EXPORT/PACKAGE/PACKAGE_BODY
     Processing object type SCHEMA_EXPORT/TABLE/STATISTICS/TABLE_STATISTICS
     . . exported "ZMY"."CF"                                  18.92 KB      82 rows
     . . exported "ZMY"."CLASSINFO"                           5.992 KB      10 rows
     . . exported "ZMY"."FFF"                                 18.92 KB      82 rows
     . . exported "ZMY"."FFF1"                                18.92 KB      82 rows
     . . exported "ZMY"."FFF2"                                18.92 KB      82 rows
     . . exported "ZMY"."K1"                                  17.25 KB      64 rows
     . . exported "ZMY"."K2"                                  17.25 KB      64 rows
     . . exported "ZMY"."K3"                                  17.25 KB      64 rows
     . . exported "ZMY"."K4"                                  17.25 KB      64 rows
     . . exported "ZMY"."QQQ"                                 18.92 KB      82 rows
     . . exported "ZMY"."SD"                                  18.92 KB      82 rows
     . . exported "ZMY"."ZQZ1"                                19.10 KB      84 rows
     . . exported "ZMY"."ZQZ2"                                19.10 KB      84 rows
     . . exported "ZQZ"."ASD"                                 18.92 KB      82 rows
     . . exported "ZQZ"."T1"                                  8.507 KB     512 rows
     . . exported "ZQZ"."T2"                                  5.046 KB       5 rows
     . . exported "ZQZ"."T6"                                  5.015 KB       1 rows
     . . exported "ZQZ"."TEST"                                5.023 KB       2 rows
     . . exported "ZQZ"."ZQZ1"                                19.10 KB      84 rows
     Master table "SYSTEM"."SYS_EXPORT_SCHEMA_01" successfully loaded/unloaded
     ******************************************************************************
     Dump file set for SYSTEM.SYS_EXPORT_SCHEMA_01 is:
     /tmp/schemas_202006111503.dmp
     Job "SYSTEM"."SYS_EXPORT_SCHEMA_01" successfully completed at Thu Jun 11 15:05:24 2020 elapsed 0 00:00:47



     INFO:expdp命令执行完成,导出文件路径为：/tmp/schemas_202006111503.dmp。

     INFO:开始传输导出文件到目标库

     schemas_202006111503.dmp                      100% 1044KB   1.0MB/s   00:00
     [oracle@11grac1 ~]$

     INFO:导出文件传输完成,目标环境路径为/tmp/schemas_202006111503.dmp

     INFO:根据导出数据库环境生成的数据表空间初始化语句如下：
     ###
     create tablespace USERS datafile '<DATAFILE_DIR>/USERS01.dbf' size 10m autoextend on;
     alter tablespace USERS add datafile '<DATAFILE_DIR>/USERS2.dbf' size 10m autoextend on;
     alter tablespace USERS add datafile '<DATAFILE_DIR>/USERS3.dbf' size 10m autoextend on;
     alter tablespace USERS add datafile '<DATAFILE_DIR>/USERS4.dbf' size 10m autoextend on;
     alter tablespace USERS add datafile '<DATAFILE_DIR>/USERS5.dbf' size 10m autoextend on;
     alter tablespace USERS add datafile '<DATAFILE_DIR>/USERS6.dbf' size 10m autoextend on;
     ###

     INFO:根据导出数据库环境生成的默认临时表空间初始化语句如下：
     ###
     create temporary tablespace USERS tempfile '<DATAFILE_DIR>/TEMP01.dbf' size 10m autoextend on;
     ###

     INFO:请根据实际情况在目标环境运行初始化表空间的语句.

     INFO:目标数据库无需添加新的用户profile策略.

     INFO:目标库导入路径目录创建语句为：
     create or replace directory mc_dump_dir as '/tmp';
     grant read,write on directory mc_dump_dir to public;

     INFO:目标库导入命令为：
     ###
     source ~/.bash_profile
     export ORACLE_SID=<SID>
     impdp "'" / as sysdba "'" schemas=ZQZ,ZMY directory=mc_dump_dir dumpfile=schemas_202006111503.dmp logfile=impdp_schemas_202006111503.log
     ###


#### 2.在11g rac环境上检查锁信息，完整输出示例

     python.exe .\ora_ops.py -i check_lock



     ###检查数据库信息:
     +---------+---------------+--------+------------+
     | INST_ID | INSTANCE_NAME | STATUS |  VERSION   |
     +---------+---------------+--------+------------+
     |    1    |    ora11g1    |  OPEN  | 11.2.0.4.0 |
     +---------+---------------+--------+------------+

     ###锁下游会话信息:
     +---------+-----+---------+----------+------------------+-------------------------------+----------------------------------+---------+---------------+---------------------------------+
     | INST_ID | SID | SERIAL# | USERNAME | BLOCKING_SESSION |             EVENT             |             PROGRAM              | MACHINE |     SQL_ID    |             SQL_TEXT            |
     +---------+-----+---------+----------+------------------+-------------------------------+----------------------------------+---------+---------------+---------------------------------+
     |    1    | 793 |   105   |   ZQZ    |        14        | enq: TX - row lock contention | sqlplus.mchz@11grac1 (TNS V1-V3) | 11grac1 | fjs09791373jz | update t1 set id =7 where id=2  |
     +---------+-----+---------+----------+------------------+-------------------------------+----------------------------------+---------+---------------+---------------------------------+

     ###锁对象信息:
     +---------+-------+-------------+-------------+---------------+----------------+-----------------+---------------+
     | INST_ID | OWNER | OBJECT_NAME | OBJECT_TYPE | ROW_WAIT_OBJ# | ROW_WAIT_FILE# | ROW_WAIT_BLOCK# | ROW_WAIT_ROW# |
     +---------+-------+-------------+-------------+---------------+----------------+-----------------+---------------+
     |    1    |  ZQZ  |      T1     |    TABLE    |     107216    |       4        |      23323      |       0       |
     +---------+-------+-------------+-------------+---------------+----------------+-----------------+---------------+

     ###锁阻塞源头会话信息:
     +---------+-----+---------+------+----------+----------------------------+-----------------------------+
     | INST_ID | SID | SERIAL# | SPID | USERNAME |          PROGRAM           |            EVENT            |
     +---------+-----+---------+------+----------+----------------------------+-----------------------------+
     |    1    |  14 |    5    | 7448 |  oracle  | oracle@11grac1 (TNS V1-V3) | SQL*Net message from client |
     +---------+-----+---------+------+----------+----------------------------+-----------------------------+

     ###锁阻塞源头会话回滚段信息:
     +---------+-----+-------+----------+----------------------+-----------+-----------+
     | INST_ID | SID | XACTS | USERNAME |         NAME         | USED_UBLK | USED_UREC |
     +---------+-----+-------+----------+----------------------+-----------+-----------+
     |    1    |  14 |   1   |   ZQZ    | _SYSSMU6_1844270496$ |     10    |    520    |
     +---------+-----+-------+----------+----------------------+-----------+-----------+
     如果你想杀掉该阻塞会话进程,可以使用以下两种方法的其中一种:

     (1).操作系统层面kill进程：

     在节点1的环境中执行命令:
     kill -9 7448

     (2).在数据库指定节点中执行以下sql来杀掉该阻塞会话:

     在节点1的数据库中执行SQL命令:
     alter system kill session'14,5,@1' immediate;


#### 3. 11g单机上设置一个逻辑泵全备任务并将备份发至远端

     python ora_ops.py -i expdp_crontab

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

#### 4. 11g单机上清理数据库日志(请使用root用户)

     python.exe .\ora_ops.py -i clean_log  -r 30           (参数配置文件未使用root用户时)
     WARNING:操作系统用户需为root!

     PS C:\F_Drive\github\ora_ops> python.exe .\ora_ops.py -i clean_log -r 30
     we will delete lofiles before 30 days before.
     now user is grid
     base_dir is /oracle/gridbase
     ADRCI: Release 11.2.0.4.0 - Production on Wed Jun 10 16:46:07 2020
     Copyright (c) 1982, 2011, Oracle and/or its affiliates.  All rights reserved.
     ADR base = "/oracle/gridbase"
     line is diag/asmtool/user_grid/host_604491092_80

     -----------
     -----------

     now directory is in /oracle/gridbase/diag/asmtool/user_grid/host_604491092_80/trace
     begin to clear files
     now directory is in /oracle/gridbase/diag/asmtool/user_grid/host_604491092_80/alert
     line is diag/asm/+asm/+ASM1

     -----------
     -----------

     now directory is in /oracle/gridbase/diag/asm/+asm/+ASM1/trace
     begin to clear files
     now directory is in /oracle/gridbase/diag/asm/+asm/+ASM1/alert
     line is diag/tnslsnr/11grac1/listener

     -----------
     -----------

     now directory is in /oracle/gridbase/diag/tnslsnr/11grac1/listener/trace
     begin to clear files
     now directory is in /oracle/gridbase/diag/tnslsnr/11grac1/listener/alert
     line is diag/tnslsnr/11grac1/lsn2

     -----------
     -----------

     now directory is in /oracle/gridbase/diag/tnslsnr/11grac1/lsn2/trace
     begin to clear files
     now directory is in /oracle/gridbase/diag/tnslsnr/11grac1/lsn2/alert
     now user is oracle
     base_dir is /oracle/app
     ADRCI: Release 11.2.0.4.0 - Production on Wed Jun 10 16:46:12 2020
     Copyright (c) 1982, 2011, Oracle and/or its affiliates.  All rights reserved.
     ADR base = "/oracle/app"
     line is diag/rdbms/ora11g/ora11g1

     -----------
     -----------

     now directory is in /oracle/app/diag/rdbms/ora11g/ora11g1/trace
     begin to clear files
     now directory is in /oracle/app/diag/rdbms/ora11g/ora11g1/alert
     line is diag/rdbms/test/test1

     -----------
     -----------

     now directory is in /oracle/app/diag/rdbms/test/test1/trace
     begin to clear files
     now directory is in /oracle/app/diag/rdbms/test/test1/alert
     line is diag/rdbms/orcl/orcl

     -----------
     -----------

     now directory is in /oracle/app/diag/rdbms/orcl/orcl/trace
     begin to clear files
     now directory is in /oracle/app/diag/rdbms/orcl/orcl/alert
     line is diag/asmtool/user_oracle/host_604491092_80

     -----------
     -----------

     now directory is in /oracle/app/diag/asmtool/user_oracle/host_604491092_80/trace
     begin to clear files
     now directory is in /oracle/app/diag/asmtool/user_oracle/host_604491092_80/alert
     line is diag/tnslsnr/11grac1/listener

     -----------
     -----------

     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener/trace
     begin to clear files
     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener/alert
     line is diag/tnslsnr/11grac1/listener2

     -----------
     -----------

     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener2/trace
     begin to clear files
     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener2/alert
     line is diag/tnslsnr/11grac1/listener_1

     -----------
     -----------

     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener_1/trace
     begin to clear files
     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener_1/alert
     line is diag/tnslsnr/11grac1/listener1

     -----------
     -----------

     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener1/trace
     begin to clear files
     now directory is in /oracle/app/diag/tnslsnr/11grac1/listener1/alert
     line is diag/tnslsnr/11grac1/dbra

     -----------
     -----------

     now directory is in /oracle/app/diag/tnslsnr/11grac1/dbra/trace
     begin to clear files
     now directory is in /oracle/app/diag/tnslsnr/11grac1/dbra/alert
     line is diag/tnslsnr/11grac1/wlb

     -----------
     -----------

     now directory is in /oracle/app/diag/tnslsnr/11grac1/wlb/trace
     begin to clear files
     now directory is in /oracle/app/diag/tnslsnr/11grac1/wlb/alert
     line is diag/tnslsnr/11grac1/test

     -----------
     -----------

     now directory is in /oracle/app/diag/tnslsnr/11grac1/test/trace
     begin to clear files
     now directory is in /oracle/app/diag/tnslsnr/11grac1/test/alert
     line is diag/diagtool/user_oracle/host_604491092_80

     -----------
     -----------

     now directory is in /oracle/app/diag/diagtool/user_oracle/host_604491092_80/trace
     begin to clear files
     now directory is in /oracle/app/diag/diagtool/user_oracle/host_604491092_80/alert
     line is diag/clients/user_dbra/host_604491092_80

     -----------
     -----------

     now directory is in /oracle/app/diag/clients/user_dbra/host_604491092_80/trace
     begin to clear files
     now directory is in /oracle/app/diag/clients/user_dbra/host_604491092_80/alert
     line is diag/clients/user_dbra/host_604491092_76

     -----------
     -----------

     now directory is in /oracle/app/diag/clients/user_dbra/host_604491092_76/trace
     begin to clear files
     now directory is in /oracle/app/diag/clients/user_dbra/host_604491092_76/alert
     line is diag/clients/user_oracle/host_604491092_80

     -----------
     -----------

     now directory is in /oracle/app/diag/clients/user_oracle/host_604491092_80/trace
     begin to clear files
     now directory is in /oracle/app/diag/clients/user_oracle/host_604491092_80/alert
     now ORACLE_SID is ora11g1
     ---------begin to clean audit file------
     auditdirectory is
     /oracle/app/admin/ora11g/adump

     -----------
     -----------

     begin to clear audit files
     ------------------------
     ------------------------
     after delete ,the  space and inodes as follows,you could refer to /tmp/space20200610.log

#### 5. 11g单机挖掘zqz.t2表在指定时间段的操作日志：
     python.exe .\ora_ops.py -i logmnr

     INFO:开始检查数据库归档是否开启:

     INFO:数据库归档已经开启!

     INFO:开始检查数据库附加日志是否开启:

     INFO:数据库最小附加日志已打开!

     INFO:开始查询指定时间内的归档信息:

     INFO:指定时间 2020-07-07 15:10:00 -- 2020-07-07 15:14:00 存在归档,
     归档日志文件数为:17 个!

     INFO:需要挖掘的归档量为0.72G

     INFO:开始归档日志文件挖掘:

     INFO:时间段2020-07-07 15:10:00 至 2020-07-07 15:14:00 归档日志挖掘成功,已生成记录表为： <SYSTEM.MC_LOGMNR_202007071519>

     INFO:获取表ZQZ.T2 在2020-07-07 15:10:00 至 2020-07-07 15:14:00 的历史信息如下：
     +---------------------+-----------+--------------------------------------------+---------------------------------------------------------------------------+
     |      TIMESTAMP      | OPERATION |                  SQL_REDO                  |                                  SQL_UNDO                                 |
     +---------------------+-----------+--------------------------------------------+---------------------------------------------------------------------------+
     | 2020-07-07 15:12:08 |   INSERT  | insert into "ZQZ"."T2"("ID") values ('3'); | delete from "ZQZ"."T2" where "ID" = '3' and ROWID = 'AAAZOSAAMAAAADEAAG'; |
     +---------------------+-----------+--------------------------------------------+---------------------------------------------------------------------------+
     | 2020-07-07 15:12:17 |   INSERT  | insert into "ZQZ"."T2"("ID") values ('3'); | delete from "ZQZ"."T2" where "ID" = '3' and ROWID = 'AAAZOSAAMAAAADEAAH'; |
     +---------------------+-----------+--------------------------------------------+---------------------------------------------------------------------------+

     INFO:如果需要删除本次挖掘信息，请手工执行<drop table system.mc_logmnr_202007071519;>


### 6. 11grac 检查表空间空间情况并给出建议：
     
     python.exe .\ora_ops.py -i tbs_check
     
     请确认您config.cfg配置中填写的是oracle用户及密码: y/n y
     请输入您要检查的数据库环境的sid： ora11g1


     this is a database of version 11.2.0.4.0


     ###########################
     here is the percentage of tablespace usage which concerning the extensibility of datafiles

     ###########################

     SYSAUX 1.97
     MC_ODC_TPS 1.43
     USERS .22
     SYSTEM 2.69

     ###########################
     below is the recommand command:

     export ORACLE_SID=ora11g1
     sqlplus / as sysdba
     alter tablespace SYSAUX add datafile '+DATA/ora11g/SYSAUX99.dbf' size 1g autoextend on;

     ###########################

     ###########################
     below is the recommand command:

     export ORACLE_SID=ora11g1
     sqlplus / as sysdba

     alter tablespace MC_ODC_TPS add datafile '+DATA/ora11g/MC_ODC_TPS100.dbf' size 1g autoextend on;
     ###########################

     ###########################
     below is the recommand command:

     export ORACLE_SID=ora11g1
     sqlplus / as sysdba
     alter tablespace USERS add datafile '+DATA/ora11g/USERS101.dbf' size 1g autoextend on;
     ###########################

     ###########################
     below is the recommand command:

     export ORACLE_SID=ora11g1
     sqlplus / as sysdba
     alter tablespace SYSTEM add datafile '+DATA/ora11g/SYSTEM102.dbf' size 1g autoextend on;
     ###########################

### 7. 11g单机 设置数据库自启动服务：

     python.exe .\ora_ops.py -i service_set

     INFO:Oracle自启动关闭使用范围:
     1.Oracle数据库单机环境
     2.Oracle数据库版本11g以上
     3.主机上存在多个版本的数据库和监听
     4.Linux 6-7


     INFO:开始配置脚本:

     INFO: 获取数据库环境服务信息:
     -----------------------INFO:DbServiceSET's get_infos function begin -----------------------
     Thu Jul 16 09:46:27 CST 2020
     ORACLE_HOME is:  /oracle/app/product/11.2.0/db_1
     ORACLE_HOME owner is:  oracle
     the ORACLE_HOME have 1 running listener(s) :LISTENER
     the ORACLE_HOME have 1 running database(s):
     -----------------------INFO:DbServiceSET's get_infos function end -----------------------
     Thu Jul 16 09:46:29 CST 2020

     请根据已知信息填写要添加的数据库服务,若不添加，请回车：
     orcl
     请根据已知信息填写要添加的监听服务,若有多个，请用逗号隔开，若不添加，请回车：


     INFO:开始执行数据库服务添加自启动：
     option:d, value orcl
     DBNAMES IS: orcl

     option:o, value /oracle/app/product/11.2.0/db_1
     ORA_HOME IS: /oracle/app/product/11.2.0/db_1

     -----------------------INFO:DbServiceSET's set_infos function begin -----------------------

     Thu Jul 16 09:46:45 CST 2020
     the rollback_script is NULL;
     the /home/oracle/startDbService.sh is not add to rollback_script!
     the rollback_script is NULL;
     the /home/oracle/stopDbService.sh is not add to rollback_script!
     -----------------------INFO:DbServiceSET's set_infos function end -----------------------
     Thu Jul 16 09:46:45 CST 2020
     -----------------------INFO:Resource set finished ----------------------- 
     Thu Jul 16 09:46:45 CST 2020
     -----------------------INFO:DbServiceSET's setOSService function begin -----------------------


     INFO:检查通过当前脚本设置的自启动资源信息：
     option:m, value l
     MODE_FLAG IS: l
     -----------------------INFO:DbServiceSET's list_start_info function begin -----------------------
     Thu Jul 16 09:46:45 CST 2020
     auto-start resource list:
     database name: orcl
     oracle home: /oracle/app/product/11.2.0/db_1
     the ORACLE_HOME owner is:  oracle
     -----------------------INFO:DbServiceSET's list_start_info function end -----------------------
     Thu Jul 16 09:46:45 CST 2020


     INFO: 配置完成后，需要通过service DbService stop或者systemctl stop DbService 停止资源一次，进行验证
     支持管理命令如下
     Linux7以下：`service DbService start｜stop｜restart`
     Linux7以上：`systemctl start｜stop｜status DbService`

#### 8.生产批量删除表的脚本

     python.exe .\ora_ops.py -i drop_tables
     请确认您config.cfg 配置中填写的是oracle用户及密码: y/n y

     ************************************************************
     本脚本用于生成用户下批量快速删除表对象的脚本
     本脚本适用于单个用户下具有几万表对象的场景

     ## 支持的操作系统和数据库版本配对
     操作系统：LINUX/AIX/UNIX
     数据库版本：Oracle 10g-19c
     源数据库架构：单机
     ************************************************************
     Table dropped.
     Table dropped.
     Table created.
     Table created.
     1
     drop table TRUNCATE_TABLE purge ;
     truncate table BIN$rAT+PSJGHTvgUzjuqMAVRw==$0;
     truncate table BIN$rAT+PSJHHTvgUzjuqMAVRw==$0;
     truncate table BIN$rAT7xwOZG7jgUzjuqMBtHg==$0;
     truncate table BIN$rAT7xwOaG7jgUzjuqMBtHg==$0;
     truncate table BIN$rATqzAAsCWrgUzjuqMA8yw==$0;
     truncate table BIN$rARDZieiQV/gUzjuqMAnkQ==$0;
     truncate table BIN$q/T2m1x5CjLgUzjuqMBrXQ==$0;
     truncate table BIN$rARDZiejQV/gUzjuqMAnkQ==$0;
     truncate table BIN$q/TuhR/3f9/gUzjuqMAArw==$0;
     truncate table BIN$q/TuhR/4f9/gUzjuqMAArw==$0;
     truncate table BIN$q/TqgC/Ee53gUzjuqMB8Vg==$0;
     truncate table BIN$q/TqgC/Fe53gUzjuqMB8Vg==$0;
     truncate table BIN$q/SNJUG0ff7gUzjuqMAIeg==$0;
     truncate table BIN$q/SNJUG1ff7gUzjuqMAIeg==$0;
     truncate table BIN$rATqzAAtCWrgUzjuqMA8yw==$0;
     truncate table BIN$rATpA6VABxrgUzjuqMCrAA==$0;
     truncate table BIN$rATpA6VBBxrgUzjuqMCrAA==$0;
     truncate table BIN$rATecPvfeR3gUzjuqMC6ng==$0;
     truncate table BIN$rATecPvgeR3gUzjuqMC6ng==$0;
     19 rows selected.


     INFO:生成truncate 用户zqz 下表脚本路径为:
     /home/oracle//parall_cmd_truncate.sh

     INFO:生成drop 用户zqz 下表脚本路径为:
     /home/oracle//parall_cmd_drop.sh