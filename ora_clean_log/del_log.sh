#!/bin/bash
###clean adrci trc trm listener.log##########

delete_time=$1
echo "we will delete logfiles before $delete_time days before."
delete_time=$[$delete_time-1]

echo "the old space and inodes as follows" >/tmp/space`date +%Y%m%d`.log
echo "space:" >>/tmp/space`date +%Y%m%d`.log
df -h  >>/tmp/space`date +%Y%m%d`.log
echo " " >>/tmp/space`date +%Y%m%d`.log
echo "inode :" >>/tmp/space`date +%Y%m%d`.log
df -i  >>/tmp/space`date +%Y%m%d`.log
echo " " >>/tmp/space`date +%Y%m%d`.log

## show the user
ps -ef|grep pmon|grep -v grep|awk '{print $1}'|uniq>/tmp/user`date +%Y%m%d`.list
cat /tmp/user`date +%Y%m%d`.list|while read user
do
echo "now user is $user"
## get the log trace
base_dir=`su - $user -c 'echo $ORACLE_BASE'`
echo "base_dir is $base_dir"
echo "set base $base_dir">/tmp/base.txt
echo " ">/tmp/path.log
chmod 777 /tmp/path.log
su - $user -c "adrci script=/tmp/base.txt"
su - $user -c "adrci exec='show homepath'|grep diag>/tmp/path.log"
cat /tmp/path.log|while read line
do
echo "line is $line"
cd $base_dir/$line/trace
echo "                       "
echo "-----------"
echo "-----------"
echo "                      "
echo "now directory is in `pwd`"
echo "begin to clear files"

find $base_dir/$line/trace -mtime +$delete_time -name "*.trc" |xargs -n 10 rm -f
find $base_dir/$line/trace -mtime +$delete_time -name "*.trm" |xargs -n 10 rm -f
find $base_dir/$line/trace -name "listener*.log" |xargs  rm -f

cd $base_dir/$line/alert
echo "now directory is in `pwd`"
find $base_dir/$line/alert -mtime +$delete_time -name "*.xml"|xargs -n 10 rm -f
done
done

########clean audit files###############
##get the sid and user with out ASM instance
ps -ef|grep pmon|grep -v grep |grep -v print |grep -v ASM|awk -F "pmon_"  '{print $2}'>/tmp/sid.log
ps -ef|grep pmon|grep -v grep |grep -v print |grep -v ASM|awk '{print $1}'>/tmp/user2.log
user_audit=`head -1 /tmp/user2.log`

cat /tmp/sid.log |while read sid
do
ora_sid=$sid 
echo "now ORACLE_SID is $ora_sid"
##generate the script to get the trace of audit file
cat > /tmp/oracle.sh <<EOF
  echo '---------begin to clean audit file------'
  export ORACLE_SID=$ora_sid
  sqlplus -s / as sysdba <<END >/tmp/audit_trace.log
  set feedback off
  set head off
  select value from v\\\$parameter where name='audit_file_dest';
END
EOF
chmod 777 /tmp/oracle.sh
su - $user_audit -c '/bin/sh /tmp/oracle.sh'
auditdir=`cat /tmp/audit_trace.log`
echo "auditdirectory is $auditdir"
echo "                       "
echo "-----------"
echo "-----------"
echo "                      "
echo "begin to clear audit files"
find $auditdir -mtime +$delete_time -name "*.aud" |xargs -n 10 rm -f
done

echo "------------------------"
echo "------------------------"
echo "after delete ,the  space and inodes as follows,you could refer to /tmp/space`date +%Y%m%d`.log "
echo " " >>/tmp/space`date +%Y%m%d`.log
echo " alter delete ,the info becomes as below" >>/tmp/space`date +%Y%m%d`.log
echo "space:" >>/tmp/space`date +%Y%m%d`.log
df -h  >>/tmp/space`date +%Y%m%d`.log
echo " " >>/tmp/space`date +%Y%m%d`.log
echo "inode :" >>/tmp/space`date +%Y%m%d`.log
df -i  >>/tmp/space`date +%Y%m%d`.log
echo "The script run completed."