
oracle 自动化运维工具

修订记录

| 作者 | 版本 | 时间       | 备注       |
| ---- | ---- | ---------- | ---------- |
| 张全针 | v1.0 | 2020/03/19 | 逻辑泵导出导入功能          |
| 张全针 | v2.1 | 2020/04/08 | 修复优化逻辑泵bug          |
| 张全针 | v2.2 | 2020/04/20 | 修复优化逻辑泵bug          |


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
                              输入你的数据库连接串：用户名/密码@ip:端口/服务名，注意请输入system用户及密码
          -m MODE, --mode MODE  数据库连接方式，可填'sysdba'或'default_auth',默认为'default_auth'
          -u USER, --user USER  操作系统oracle用户,默认为'oracle'
          -p PASSWORD, --password PASSWORD
                              操作系统oracle用户密码
          -P SSH_PORT, --ssh_port SSH_PORT
                              操作系统ssh的端口号,默认为22
          -d DEGREE, --degree DEGREE
                              导入导出时的并行度,默认为1，即不开启并行
          -r RUN_EXPDP, --run_expdp RUN_EXPDP
                              在导出环境运行导出命令，默认为不运行
          -path PATH, --path PATH
                              导入导出文件存放路径
          -db_path DATAFILE_PATH, --datafile_path DATAFILE_PATH
                              生成导入库初始化表空间时用到的数据文件存放路径，默认为<DATAFILE_DIR>
          -s SYNC_OBJ, --sync_obj SYNC_OBJ
                              想要导出的对象，例如，全库：full_expdp | 多用户：test,test1 | 多表：test.t1,test.t2,test2.t10
          -i {check_instance,expdp,create_dir}, --item {check_instance,expdp,create_dir,check_lock}
                              expdp:数据库导出|check_instance:检查数据库|create_dir:创建数据库导入导出目录
                              check_lock:数据库锁检查

### 使用举例

#### 1.在11grac环境上导出zqz.t1,zqz.t2,hzmc.t3 多表,并指定并发度为2

     python ora_ops.py -c sys/oracle@192.168.238.35:1521/ora11g -u oracle -p oracle -s zqz.t1,zqz.t2 -i expdp  -d 2 -path /u01 -db_path /data

#### 2.在11grac环境上导出zqz,hzmc 多用户，并直接执行导出语句

     python ora_ops.py -c zqz/zqz@192.168.238.35:1521/ora11g -u oracle -p oracle -s zqz,hzmc -i expdp  -d 2 -path /u01 -db_path /data -r

#### 3.在11grac环境上导出全库

     python ora_ops.py -c zqz/zqz@192.168.238.35:1521/ora11g -u oracle -p oracle -s full_expdp -i expdp -d 2 -path /u01 -db_path /data

#### 4.在11grac环境上仅创建数据库导入导出目录

     python ora_ops.py -c system/oracle@192.168.238.35:1521/ora11g -u oracle -p oracle -i create_dir -path /u01

#### 5.在12c 单机CDB环境上导出zqz用户,ssh端口号为9022，完整输出示例

     python ora_ops.py -c system/oracle@192.168.238.29:1521/ora12c1 -u ora12cr1 -p oracle -s zqz -i expdp -P 9022 -d 2 -path /home/ora12cr1 -db_path /datafile -r

          INFO:检查数据库信息 system/oracle@192.168.238.29:1521/ora12c1:
          +---------+---------------+--------+------------+
          | INST_ID | INSTANCE_NAME | STATUS |  VERSION   |
          +---------+---------------+--------+------------+
          |    1    |    ora12c1    |  OPEN  | 12.1.0.2.0 |
          +---------+---------------+--------+------------+

          INFO:system/oracle@192.168.238.29:1521/ora12c1
          数据库目录MC_DUMP_DIR：/home/ora12cr1 创建成功
          +-------+----------------+----------------+---------------+
          | OWNER | DIRECTORY_NAME | DIRECTORY_PATH | ORIGIN_CON_ID |
          +-------+----------------+----------------+---------------+
          |  SYS  |  MC_DUMP_DIR   | /home/ora12cr1 |       0       |
          +-------+----------------+----------------+---------------+

          INFO:导出对象用户的默认表空间及默认临时表空间信息如下：
          +----------+--------------------+----------------------+
          | USERNAME | DEFAULT_TABLESPACE | TEMPORARY_TABLESPACE |
          +----------+--------------------+----------------------+
          |   ZQZ    |        ZQZ         |         TEMP         |
          +----------+--------------------+----------------------+

          INFO:根据导出数据库环境生成的数据表空间初始化语句如下：
          ###
          create tablespace ZQZ datafile '/datafile/ZQZ01.dbf' size 10m autoextend on;
          ###

          INFO:根据导出数据库环境生成的默认临时表空间初始化语句如下：
          ###
          create temporary tablespace ZQZ tempfile '/datafile/TEMP01.dbf' size 10m autoextend on;
          ###

          INFO:请根据实际情况在目标环境运行初始化表空间的语句。

          INFO:根据导出数据库环境生成的用户profile策略ddl语句如下：
          ###

          CREATE PROFILE "PROFILE_TEST1"
          LIMIT
               COMPOSITE_LIMIT DEFAULT
               SESSIONS_PER_USER 5
               CPU_PER_SESSION DEFAULT
               CPU_PER_CALL DEFAULT
               LOGICAL_READS_PER_SESSION DEFAULT
               LOGICAL_READS_PER_CALL DEFAULT
               IDLE_TIME 1
               CONNECT_TIME DEFAULT
               PRIVATE_SGA DEFAULT
               FAILED_LOGIN_ATTEMPTS DEFAULT
               PASSWORD_LIFE_TIME DEFAULT
               PASSWORD_REUSE_TIME DEFAULT
               PASSWORD_REUSE_MAX DEFAULT
               PASSWORD_VERIFY_FUNCTION DEFAULT
               PASSWORD_LOCK_TIME DEFAULT
               PASSWORD_GRACE_TIME DEFAULT


          INFO:导出对象预估大小：0.0625 M

          INFO:导出环境的逻辑CPU数为4,推荐并行度应不超过8,用户选择并行度为2

          INFO:导出命令为：
          ###
          source ~/.bash_profile
          export ORACLE_SID=ora12c1
          expdp "'" / as sysdba "'" schemas=ZQZ directory=mc_dump_dir parallel=2 dumpfile=schemas_202003231412_%U.dmp logfile=schemas_202003231412.log
          ###

          INFO:导入命令为：
          ###
          source ~/.bash_profile
          export ORACLE_SID=<SID>
          impdp "'" / as sysdba "'" schemas=ZQZ directory=mc_dump_dir parallel=2   dumpfile=schemas_202003231412_%U.dmp logfile=impdp_schemas_202003231412.log
          ###

          INFO：命令运行中，请关注本地ora_ops.log或数据库环境下的导出日志

          Export: Release 12.1.0.2.0 - Production on Mon Mar 23 14:11:17 2020

          Copyright (c) 1982, 2014, Oracle and/or its affiliates.  All rights reserved.

          Connected to: Oracle Database 12c Enterprise Edition Release 12.1.0.2.0 - 64bit Production
          With the Partitioning, OLAP, Advanced Analytics and Real Application Testing options
          Starting "SYS"."SYS_EXPORT_SCHEMA_01":  "/******** AS SYSDBA" schemas=ZQZ directory=mc_dump_dir parallel=2 dumpfile=schemas_202003231412_%U.dmp logfile=schemas_202003231412.log
          Estimate in progress using BLOCKS method...
          Processing object type SCHEMA_EXPORT/TABLE/TABLE_DATA
          Total estimation using BLOCKS method: 64 KB
          Processing object type SCHEMA_EXPORT/USER
          Processing object type SCHEMA_EXPORT/SYSTEM_GRANT
          Processing object type SCHEMA_EXPORT/ROLE_GRANT
          . . exported "ZQZ"."T1"                                  17.90 KB      39 rows
          Processing object type SCHEMA_EXPORT/DEFAULT_ROLE
          Processing object type SCHEMA_EXPORT/PRE_SCHEMA/PROCACT_SCHEMA
          Processing object type SCHEMA_EXPORT/TABLE/TABLE
          Processing object type SCHEMA_EXPORT/TABLE/STATISTICS/TABLE_STATISTICS
          Processing object type SCHEMA_EXPORT/STATISTICS/MARKER
          Master table "SYS"."SYS_EXPORT_SCHEMA_01" successfully loaded/unloaded
          ******************************************************************************
          Dump file set for SYS.SYS_EXPORT_SCHEMA_01 is:
          /home/ora12cr1/schemas_202003231412_01.dmp
          /home/ora12cr1/schemas_202003231412_02.dmp
          Job "SYS"."SYS_EXPORT_SCHEMA_01" successfully completed at Mon Mar 23 14:11:52 2020 elapsed 0 00:00:32



          INFO:命令执行完成。
          PS C:\F_Drive\github\ora_expdp_impdp>
