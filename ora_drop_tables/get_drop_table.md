# oracle-get-drop-table
脚本用于生成用户下批量快速删除表对象的脚本
脚本适用于单个用户下具有几万表对象的场景
##修订记录
| 作者 | 版本 | 时间 | 备注 |
| --- | --- | --- | --- |
| 张衡 | v2.7 | 2020-07-08 | readme初版 |
|   |   |   | |


## 支持的操作系统和数据库版本配对
操作系统：LINUX/AIX/UNIX
数据库版本：Oracle 10g-19c
源数据库架构：单机

## 使用说明
###前期准备工作
1.上传脚本至服务器
2.修改脚本前部的参数

###脚本前部参数说明
sid=orcl1  #实例名
script_dir=/home/oracle/hzmc/drop #脚本目录
user=vivien #删除用户名
pass=oracle #删除用户的密码
ORACLE_HOME=/oracle/app/product/11.2.0.3/db_1 #Oracle Home 目录
gap=10000  #单个脚本包含对象的函数

###脚本执行样例
`sh get_drop_table.sh  `
