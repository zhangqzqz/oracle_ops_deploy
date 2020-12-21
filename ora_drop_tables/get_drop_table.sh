#!/bin/bash 
####################modify below section################
sid=$1
script_dir=$2
user=$3
pass=$4
ORACLE_HOME=$5
gap=$6
####################modify above section################
source ~/.bash_profile
export ORACLE_SID=$sid
export ORACLE_HOME=$ORACLE_HOME
owner=`echo $user| tr a-z A-Z`
cmd_dir=${script_dir}/${user}
mkdir -p ${cmd_dir}

sqlplus -S ${owner}/${pass} <<EOF 
set pages 0
drop table drop_table;
drop table truncate_table; 
create table  truncate_table  as select rownum id, 'truncate table '||segment_name||';' truncate_cmds from user_segments where segment_type='TABLE' and BYTES is not null; 
create table  drop_table  as select rownum id, 'drop table '||table_name ||' purge ;' drop_cmds from user_tables ;
spool ${cmd_dir}/seq.log
select listagg(id,' ')  within group (order by id)  from drop_table a ,(select count(*)/${gap}  max from drop_table )b
where id<b.max+1;
spool off
exit
EOF
 

cat >${cmd_dir}/run.sh <<EOF_1
PATH=\$PATH:\$HOME/bin 
export ORACLE_HOME=${ORACLE_HOME}
export PATH=\$PATH:\$ORACLE_HOME/bin  
export ORACLE_SID=${sid}
sqlplus ${owner}/${pass} <<EOF &
\$1
exit
EOF
EOF_1

chmod +x ${cmd_dir}/run.sh

>${cmd_dir}/parall_cmd_drop.sh
>${cmd_dir}/parall_cmd_truncate.sh
for  i in `cat ${cmd_dir}/seq.log`
do 
    export ORACLE_SID=$sid
    sqlplus -S ${owner}/${pass}  <<EOF
set pages 0
set newpage none
set head off
spool ${cmd_dir}/${owner}_drop_${i}.sql 
select drop_cmds from drop_table where id between (${i}-1)*${gap} and ${i}*${gap}-1;
spool off
spool ${cmd_dir}/${owner}_truncate_${i}.sql 
select truncate_cmds from truncate_table where id between (${i}-1)*${gap} and ${i}*${gap}-1;
spool off
EOF
echo "nohup sh ${cmd_dir}/run.sh  @${owner}_drop_${i}.sql & " >>${cmd_dir}/parall_cmd_drop.sh
echo "nohup sh ${cmd_dir}/run.sh  @${owner}_truncate_${i}.sql & " >>${cmd_dir}/parall_cmd_truncate.sh
done

chmod +x ${cmd_dir}/parall_cmd_truncate.sh
chmod +x ${cmd_dir}/parall_cmd_drop.sh
