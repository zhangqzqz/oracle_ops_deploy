# -*- coding:utf-8 -*-

'''
the tool for oracle lock lock
'''
import logging
from connection.ora_conn import ora_all
from method import check_instance,res_table,log

@log
def lock_ops(db_args,mode):

    # some sql
    get_locksession_sql = "select b.inst_id,b.sid,b.serial#,b.username,b.blocking_session,b.event,b.program,b.machine,a.sql_id,a.sql_text from gv$sql a,gv$session b ,gv$session bb \
            where a.sql_id=b.sql_id and   a.inst_id=b.inst_id and  b.final_blocking_session is not null \
            and b.final_blocking_instance = bb.inst_id \
            and b.final_blocking_session = bb.sid \
            and b.sid <> bb.sid"
    get_lockrow_sql = "select a.inst_id,b.owner,b.object_name,b.object_type,a.row_wait_obj#, a.row_wait_file#, a.row_wait_block#, a.row_wait_row# \
            from gv$session a,gv$session aa,dba_objects b \
                where  a.row_wait_obj#=b.object_id \
                and a.final_blocking_session is not null \
                and a.final_blocking_instance = aa.inst_id \
                and a.final_blocking_session = aa.sid \
                and a.sid <> aa.sid"
    get_bk_sql = "select a.INST_ID,b.sid,b.serial#,a.spid,a.username,a.program,b.event from gv$process a,gv$session b \
            where a.inst_id=b.inst_id and a.addr=b.paddr and (a.inst_id,b.sid) in \
                (select s.final_blocking_instance,s.blocking_session from gv$session s,gv$session ss where s.final_blocking_session is not null \
            and s.final_blocking_instance = ss.inst_id \
            and s.final_blocking_session = ss.sid \
            and s.sid <> ss.sid)"

    get_undo_seg_sql = "select s.inst_id,s.sid,r.xacts,s.username, u.name,t.used_ublk,t.used_urec \
            from gv$transaction t, gv$rollstat r, v$rollname u, gv$session s \
            where s.taddr = t.addr \
            and t.xidusn = r.usn \
            and r.usn = u.usn and s.inst_id=r.inst_id and s.sid in ( \
                select s1.blocking_session from gv$session s1,gv$session s2 where s1.final_blocking_session is not null  \
                and s1.final_blocking_instance = s2.inst_id \
                and s1.final_blocking_session = s2.sid \
                and s1.sid <> s2.sid) \
            order by t.used_urec"

    check_instance(db_args,mode)

    print("\n###锁下游会话信息:")
    lock_session_info,lock_session_title = ora_all(db_args,get_locksession_sql,mode)
    if lock_session_info!=[]:
        lock_table = res_table(lock_session_info,lock_session_title)
        print(lock_table)

        print("\n###锁对象信息:")
        lock_row_info,lock_row_title = ora_all(db_args,get_lockrow_sql,mode)
        lock_row_table = res_table(lock_row_info,lock_row_title)
        print(lock_row_table)

        print("\n###锁阻塞源头会话信息:")
        lock_bk_info,lock_bk_title = ora_all(db_args,get_bk_sql,mode)
        lock_bk_table = res_table(lock_bk_info,lock_bk_title)
        print(lock_bk_table)

        print("\n###锁阻塞源头会话回滚段信息:")
        undo_info,undo_title = ora_all(db_args,get_undo_seg_sql,mode)
        undo_table = res_table(undo_info,undo_title)
        print(undo_table)

        kill_sql_list = []
        kill_pid_list = []
        inst_id_list = []
        print("如果你想杀掉该阻塞会话进程,可以使用以下两种方法的其中一种:\n\n(1).操作系统层面kill进程：")
        for bk in lock_bk_info:
            inst_id = bk[0]
            sid = bk[1]
            spid = bk[3]
            serial_id = bk[2]
            kill_sql = (f"alter system kill session'{sid},{serial_id},@{inst_id}' immediate;")
            kill_sql_list.append([inst_id,kill_sql])
            kill_pid_list.append([inst_id,spid])
            inst_id_list.append(inst_id)
        inst_id_list = list(set(inst_id_list))
        for inst_id in inst_id_list:
            print(f"\n在节点{inst_id}的环境中执行命令:")
            for  pid in kill_pid_list :
                if pid[0] == inst_id:
                    spid = pid[1]
                    print(f"kill -9 {spid}")
        print(f"\n(2).在数据库指定节点中执行以下sql来杀掉该阻塞会话:")
        for inst_id in inst_id_list:
            print(f"\n在节点{inst_id}的数据库中执行SQL命令:")
            for  sql in kill_sql_list:
                if sql[0] == inst_id:
                    sql_str = sql[1]
                    print(sql_str)
    else:
        print("本数据库未发现锁.\n")
