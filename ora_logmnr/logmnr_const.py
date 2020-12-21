#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
SQL_LOG_MNR = {
    
    "GET_ARCHIVELOG_STATUS_SQL":
    '''
    select log_mode from v$database
    ''',

    "GET_SUPPERLOG_STATUS_SQL":
    '''
    SELECT supplemental_log_data_min min FROM v$database
    ''',

    "GET_ARCHIVELOG_SQL":
    '''
    select name from v$archived_log 
    where
    next_time>=to_date('%s','yyyy-mm-dd hh24:mi:ss')
    and first_time<=to_date('%s','yyyy-mm-dd hh24:mi:ss') 
    and standby_dest='NO' and name <> 'None'
    ''',

    "GET_ARCHIVELOG_SIZE_SQL":
    '''
    select round(sum(blocks * block_size)/1024/1024/1024,2) from v$archived_log 
    where
    next_time>=to_date('%s','yyyy-mm-dd hh24:mi:ss')
    and first_time<=to_date('%s','yyyy-mm-dd hh24:mi:ss') 
    and standby_dest='NO'
    order by FIRST_TIME
    ''',

    "LOGMNR_NEW_LOGFILE_SQL":
    '''
    begin
        DBMS_LOGMNR.ADD_LOGFILE(logfilename => '%s',options => dbms_logmnr.new);

    ''',

    "LOGMNR_ADD_LOGFILE_SQL":
    '''
        DBMS_LOGMNR.ADD_LOGFILE(logfilename => '%s',options => dbms_logmnr.addfile);

    ''',

    "LOGMNR_START_SQL":
    '''
        DBMS_LOGMNR.START_LOGMNR(OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG);

    ''',

    "CREATE_LOGMNR_TABLE_SQL":
    '''
    create table mc_logmnr_%s as select * from v$logmnr_contents
    ''',

    "GET_LOGMNR_RES_SQL":
    '''
    select TIMESTAMP,OPERATION,SQL_REDO,SQL_UNDO from %s
    where SEG_NAME='%s' and SEG_OWNER='%s' 
    order by TIMESTAMP
    ''',

    "LOGMNR_END_SQL":
    '''
    begin DBMS_LOGMNR.END_LOGMNR; end;
    '''



}
