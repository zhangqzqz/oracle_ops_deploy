# 004-Oracle-自启动关闭脚本

| 时间 | 版本 | 作者 |
| --- | --- | --- |
| 2020-04-05 | v1.0 | 张衡 |
| 2020-04-10 | v1.1 | 张衡 |
| 2020-04-14 | v1.2 | 张衡 |

##适配范围
1.Oracle数据库单机环境
2.Oracle数据库版本11g以上 
3.主机上存在多个版本的数据库和监听
4.Linux 6-7

##功能
1.查询当前主机上oracle软件目录，启动的监听以及库信息
2.设置Oracle软件目录下的指定数据库和监听自启动,保证资源不重复的情况下，可以进行多次添加
3.可以通过操作系统的服务接口进行管理
4.可以查看当前已经通过脚本设定自启动的资源

##版本迭代说明
###v1.0
1.查看当前主机上Oracle软件目录，动的监听以及库信息
2.可以单次设置Oracle软件目录下的指定数据库和监听自启动
3.可以通过操作系统的服务接口进行管理

###v1.1
1.支持脚本多次进行添加自启动资源
2.支持已通过脚本设置自启动资源信息输出
3.脚本参数描述进行迭代
4.添加部分参数检查
5.更新Readme

###v1.2
1.修改帮助说明

##使用方法
上传脚本
0.查看帮助说明
  `sh DbServiceSet.sh -help`
1.查看当前主机的Oracle软件目录，监听信息和库信息
  `sh DbServiceSet.sh`
2.根据列出的信息内容，手工选择需要开机自启动的内容
  2.1 批量添加数据库和监听资源
  `sh DbServiceSet.sh -d ora19c -o /oracle/app/oracle/product/12201/dbhome_1 [-l listener1,listener2]`
  2.2 批量添加数据库资源
  `sh DbServiceSet.sh -d ora19c -o /oracle/app/oracle/product/12201/dbhome_1`
  2.3 批量添加监听资源
   `sh DbServiceSet.sh -o /oracle/app/oracle/product/12201/dbhome_1 -l listener1,listener2`
3.查看通过当前脚本设置的自启动资源信息
  `sh  DbServiceSet.sh -m l`
4可以通过service/systemctl进行管理(启动/停止) 
  配置完成后，需要通过service DbService stop或者systemctl stop DbService 停止资源一次，进行验证
  支持管理命令如下
Linux7以下：`service DbService start｜stop｜restart`
Linux7以上：`systemctl start｜stop｜status DbService`

##脚本尚未支持
1.未对需要自启动的资源进行是否存在，是否正常等校验
2.未对进行添加自启动的资源进行是否重复添加的校验

