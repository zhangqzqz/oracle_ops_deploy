#!/bin/bash
# 2020-05-14 version 1 
# author:troy xie
# support single directory,later version will support multiple directory
# if database is pdb,attention this ,the script will calculate all the pdb space including mount database ;
# then if tablespace of the mount database higher than the use ration,
# then,the scirpt will show error ORA-01219: database or pluggable database not open: queries allowed on fixed
 
export LANG=en_US.UTF-8
source ~/.bash_profile
ORACLE_SID=$1

version=`sqlplus -v |awk '{print $3}'|awk -F "." '{print $1}'|awk '{printf "%s",$1}'|sed '/ /g'`
full_version=`sqlplus -v |awk '{print $3}'|awk '{printf "%s",$1}'|sed '/ /g'`
#you can change here ,20 means free more 20% we would show the recommand command
free_gt_ratio=1

#the percentage
tbs_used_ratio=1


##function func_for_11_12_nopdb##
######################################################################
function func_for_11_12_nopdb(){

        #continue to judge whether it is a rac environment
        cat > /tmp/get_first_character.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba  <<"eof"  
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select substr(file_name,0,1) from dba_data_files where rownum<2;
exit
eof
EOF
        #get the diskgroup dir name or the local dir,both ok
        #########temporarily support only single directory,the later release will support all tablespace
        
        cat > /tmp/get_file_id.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select max(file_id) from dba_data_files;
exit
eof
EOF


        cat > /tmp/get_no_pdb_space.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4 
with undotbs as
 (select a.ts#, a.name, b.contents
    from v\$tablespace a, dba_tablespaces b
   where a.name = b.tablespace_name) select a.name, trunc(b.used_space / c.max_size * 100,2) || ' & ' used_percent  from undotbs a,
       dba_tablespace_usage_metrics b,
       (select tablespace_id, sum(file_maxsize) max_size
          from v\$filespace_usage
         group by tablespace_id) c
 where a.name = b.tablespace_name(+)
   and a.ts# = c.tablespace_id(+)
   and a.contents not in ('UNDO', 'TEMPORARY') and used_percent>$tbs_used_ratio;
exit
eof
EOF

    echo ""
    echo "this is a database of version $full_version"
    echo ""
    tbs_result=`/bin/sh /tmp/get_no_pdb_space.sh`
    if [ "$tbs_result" = "" ]; then 
        echo ""
        echo "check complete,the tablespace space is free enough";
        echo ""
    else 
        #show the ratio of tablespace 
        echo "###########################"
        echo "here is the percentage of tablespace usage which concerning the extensibility of datafiles "
        echo $tbs_result|sed 's/& /\n/g'|sed 's/&//g' >/tmp/result_row1.txt
        echo "###########################"
        cat /tmp/result_row1.txt 
        #because here are multiple tablespaces , so ween need to make a circle
        maxfileid=`/bin/sh /tmp/get_file_id.sh|awk '{printf "%s",$1}'|sed '/ /g'`
        
        for tbs in `awk '{print $1}' /tmp/result_row1.txt`;
        do
        #get some information
        first_character=`/bin/sh /tmp/get_first_character.sh`
        
        maxfileid=`expr $maxfileid + 1`
        
 
            #if ASM,judge space enough or not 
        if [ "$first_character" = '+' ];then    
            #get the asmspace ratio,if free enough ,show the sql that adding datafiles
            cat > /tmp/get_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba  <<"eof"  
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select  distinct(substr(file_name,1,instr(file_name,'/',1)-1)) from dba_data_files where tablespace_name='$tbs' and rownum<2;
exit
eof
EOF
            cat > /tmp/get_full_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select  distinct(substr(file_name,1,instr(file_name,'/',-1))) from dba_data_files where tablespace_name='$tbs' and file_name like '%$front_dir%' and  rownum<2;
exit
eof
EOF
            
            front_dir=`/bin/sh /tmp/get_dir.sh`
            full_dir=`/bin/sh /tmp/get_full_dir.sh`
            
            cat > /tmp/asm_dir_free_ratio.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select trunc(free_mb/total_mb*100)  from v\$asm_diskgroup where '+'||name='$front_dir';
exit
eof
EOF
            asm_dir_free_ratio=`/bin/sh /tmp/asm_dir_free_ratio.sh`

            ##echo "ratio=$asm_dir_free_ratio"
            if [ $asm_dir_free_ratio -gt $free_gt_ratio ];then
                #print the sql
                echo "###########################"
                echo " below is the recommand command: "
                echo ""
                echo " export ORACLE_SID=$ORACLE_SID"
                echo " sqlplus / as sysdba"
                echo " alter tablespace $tbs add datafile '${full_dir}${tbs}${maxfileid}.dbf' size 1g autoextend on;"
                echo ""###########################""
            # space is not enough                  
            else 
                echo "your asm free space $front_dir is lower than 20%,take attention">>/tmp/result.txt
            fi

        #if single ,judge local system is enough or not 
        else
            local_dir_use_ratio=`df $front_dir -HP|awk '{print $5}'|sed -n '2p' |sed 's/.$//'`
            if [ $local_dir_use_ratio -gt $free_gt_ratio ];then
                #print the sql
            cat > /tmp/get_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba  <<"eof"  
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select  distinct(substr(file_name,1,instr(file_name,'/',-1))) from dba_data_files where tablespace_name='$tbs' and rownum<2;
exit
eof
EOF
            cat > /tmp/get_full_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select  distinct(substr(file_name,1,instr(file_name,'/',-1))) from dba_data_files where tablespace_name='$tbs' and file_name like '%$front_dir%' and  rownum<2;
exit
eof
EOF
            
            front_dir=`/bin/sh /tmp/get_dir.sh`
            full_dir=`/bin/sh /tmp/get_full_dir.sh`
            
            cat > /tmp/asm_dir_free_ratio.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select trunc(free_mb/total_mb*100)  from v\$asm_diskgroup where '+'||name='$front_dir';
exit
eof
EOF
                echo "##########################"
                echo " below is the recommand command: "
                echo ""
                echo " export ORACLE_SID=$ORACLE_SID"
                echo " sqlplus / as sysdba"
                echo " alter tablespace $tbs add datafile '${fill_dir}${tbs}_${maxfileid}.dbf' size 1g autoextend on;"
                echo "###########################"
                exit
             # not enough free space  
            else 
                echo "your local free space of directory ${full_dir} is lower than 20%,take attention">>/tmp/result.txt
            fi
        fi
        done            
    fi
}


#######function func_for_12c_pdb()
############################################################################################################
function func_for_12c_pdb(){

cat > /tmp/get_pdb_space.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4 
col db_name for a20
with undotbs as
 (select nvl(t.name, 'CDB$ROOT') as DB_NAME,a.ts#, a.name, b.status, b.contents from v\$tablespace a, dba_tablespaces b,v\$pdbs t
   where a.name = b.tablespace_name and t.con_id=a.con_id  ) select db_name,a.name, trunc(b.used_space / c.max_size * 100,2) || ' & ' used_percent 
  from undotbs a,
       dba_tablespace_usage_metrics b,
       (select tablespace_id, sum(file_maxsize) max_size
          from v\$filespace_usage
         group by tablespace_id) c
 where a.name = b.tablespace_name(+)
   and a.ts# = c.tablespace_id(+)
   and a.contents not in ('UNDO', 'TEMPORARY')  and  used_percent>$tbs_used_ratio;
exit
eof
EOF
    echo ""
    echo "this is a database of version $full_version"
    echo ""
    tbs_result=`/bin/sh /tmp/get_pdb_space.sh`
    if [ "$tbs_result" = "" ]; then 
        echo ""
        echo "check complete,the tablespace space is free enough";
        echo ""
    else 
        #show the ratio of tablespace 
        echo "###########################"
        echo "here is the percentage of tablespace usage which concerning the extensibility of datafiles "
        echo $tbs_result|sed 's/& /\n/g'|sed 's/&//g' >/tmp/result_row1.txt
        echo "###########################"
        cat /tmp/result_row1.txt 
        #because here are multiple tablespaces , so ween need to make a circle
        cat /tmp/result_row1.txt|while read line
        do
            pdb_name=`echo $line|awk '{print $1}'`
            tbs=`echo $line|awk '{print $2}'`
                #continue to judge whether it is a rac environment
            cat > /tmp/get_first_character.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba  <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container=$pdb_name;
select substr(file_name,0,1) from dba_data_files where rownum<2;
exit
eof
EOF
        #get the diskgroup dir name or the local dir,both ok
        #########temporarily support only single directory,the later release will support all tablespace
        
            cat > /tmp/get_file_id.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container=$pdb_name;
select max(file_id) from dba_data_files;
exit
eof
EOF
            
           #get some information
            first_character=`/bin/sh /tmp/get_first_character.sh`
            maxfileid=`/bin/sh /tmp/get_file_id.sh|awk '{printf "%s",$1}'|sed '/ /g'`


            #if ASM,judge space enough or not 
            if [ "$first_character" = '+' ];then    
            #get the asmspace ratio,if free enough ,show the sql that adding datafiles
                cat > /tmp/get_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba  <<"eof"  
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container=$pdb_name;
select  distinct(substr(file_name,1,instr(file_name,'/',1)-1)) from dba_data_files where tablespace_name='$tbs' and rownum<2;
exit
eof
EOF
                front_dir=`/bin/sh /tmp/get_dir.sh`
                cat > /tmp/get_full_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container=$pdb_name;
select  distinct(substr(file_name,1,instr(file_name,'/',-1))) from dba_data_files where tablespace_name='$tbs' and file_name like '%$front_dir%' and  rownum<2;
exit
eof
EOF
                full_dir=`/bin/sh /tmp/get_full_dir.sh`
                
                cat > /tmp/asm_dir_free_ratio.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container=$pdb_name;
select trunc(free_mb/total_mb*100)  from v\$asm_diskgroup where '+'||name='$front_dir';
exit
eof
EOF
                asm_dir_free_ratio=`/bin/sh /tmp/asm_dir_free_ratio.sh`


                ##echo "ratio=$asm_dir_free_ratio"
                if [ ${asm_dir_free_ratio} -gt $free_gt_ratio ];then
                    #print the sql
                    
                    echo ""###########################""
                    echo " below is the recommand command: "
                    echo ""
                    echo " export ORACLE_SID=${ORACLE_SID}"
                    echo " sqlplus / as sysdba"
                    echo " alter session set container=${pdb_name}"
                    echo " alter tablespace $tbs add datafile '${full_dir}${tbs}_${maxfileid}.dbf' size 1g autoextend on;"
                    echo ""###########################""
                # space is not enough                  
                else 
                    echo ""
                    echo "your asm free space $full_dir is lower than 20%,take attention">>/tmp/result.txt
                    echo ""
                fi

            #if single ,judge local system is enough or not 
            else
                local_dir_use_ratio=`df $front_dir -HP|awk '{print $5}'|sed -n '2p' |sed 's/.$//'`
                if [ ${local_dir_use_ratio} -gt $free_gt_ratio ];then
                #print the sql
                cat > /tmp/get_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba  <<"eof"  
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container= $pdb_name ;
select  distinct(substr(file_name,1,instr(file_name,'/',-1))) from dba_data_files where tablespace_name='$tbs' and rownum<2;
exit
eof
EOF
                front_dir=`/bin/sh /tmp/get_dir.sh`
            
                cat > /tmp/asm_dir_free_ratio.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container= $pdb_name ;
select trunc(free_mb/total_mb*100)  from v\$asm_diskgroup where '+'||name='$front_dir';
exit
eof
EOF

                cat > /tmp/get_full_dir.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba <<"eof"
set heading off feedback off pagesize 0 verify off echo off numwidth 4
alter session set container=$pdb_name;
select  distinct(substr(file_name,1,instr(file_name,'/',-1))) from dba_data_files where tablespace_name='$tbs' and file_name like '%$front_dir%' and  rownum<2;
exit
eof
EOF
                full_dir=`/bin/sh /tmp/get_full_dir.sh`


                echo "##########################"
                echo " below is the recommand command: "
                echo ""
                echo " export ORACLE_SID=${ORACLE_SID}"
                echo " sqlplus / as sysdba"
                echo "alter session set container=${pdb_name};"
                echo " alter tablespace ${tbs} add datafile '${full_dir}${tbs}_${maxfileid}.dbf' size 1g autoextend on;"
                echo "###########################"
                exit
                # not enough free space  
                else 
                    echo "your local free space of directory ${full_dir} is lower than 20%,take attention">>/tmp/result.txt
                fi
            fi
        done            
    fi
}

######### main procedure #########################

echo "">/tmp/result.txt 
if [ $version -lt 12 ]; then
    func_for_11_12_nopdb
else
    cat > /tmp/judge_pdb.sh<<EOF 
export ORACLE_SID=$ORACLE_SID
sqlplus -S / as sysdba  <<"eof"  
set heading off feedback off pagesize 0 verify off echo off numwidth 4
select cdb from v$database;
exit
eof
EOF
    chmod 755 /tmp/judge_pdb.sh
    #if none-cdb
    judge_pdb=`/tmp/judge_pdb.sh`
    if [ "${judge_pdb}" = 'NO' ];then
        echo ""
        echo "this is a none-pdb database "
        echo ""
        func_for_11_12_nopdb
    #if cdb
    else
        echo ""
        echo "this is a pdb database "
        echo ""
        func_for_12c_pdb
        echo ""
    fi
 fi
 cat /tmp/result.txt|uniq
