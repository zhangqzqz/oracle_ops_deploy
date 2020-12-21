#!/bin/bash
#created @ 2020-03-28
#auth: vivien_zh
#version infos:
#v1.0 1.list oracle_home/listener/database infos
#     2.choice U want auto start by host database and listener
#v1.1 1.Can be executed multiple times
#     2.Optimized help description
#     3.Add parameter combination check


export LANG=en_US.UTF-8
unset MAILCHECK
while getopts "d:h:l:m:o:" option;
do
    case "$option" in  
        d)
            DBNAMES=$OPTARG
            echo "option:d, value $OPTARG"
            echo "DBNAMES IS: $DBNAMES"
            ;;

        h)
            #echo "option:h, value $OPTARG"            
            echo "Usage: args  [-d] [-help] [-l] [-m] [-o] " 
            echo "-d means: to set the DBNAME auto-start" 
            echo "-help means: to get helpinfo"
            echo "-l means: set the listener(s) auto start"
            echo "-m means: if U want GET running resource [database|listener] infos,set g|G;"
            echo "          U want SET resource [database|listener] auto-start ,set s|S;" 
            echo "          U want kown which resources already set in auto-start ,set l|L;" 
            echo "          default mode is [g]"
            echo "-o means: the DB's ORACLE_HOME" 
            echo ""
            echo "If run the script first on this node,by the following steps to set DbService(db&listener) auto-start"
            echo "step1:sh DbServiceSet.sh [-m g]"
            echo "U will see the running ORACLE_HOMES with listeners infos"
            echo "step2:sh DbServiceSet.sh -m s -d orcl,test -o /oracle/app/oracle/product/11.2.0/dbhome_1 -l listener1,listener2"
            echo "IF U need add new resource database to auto-start"
            echo "sh DbServiceSet.sh  -m s -d newdb -o /oracle/app/oracle/product/11.2.0/dbhome_1 "
            echo "IF U need add new resource listener to auto-start"
            echo "sh DbServiceSet.sh -m s -o /oracle/app/oracle/product/11.2.0/dbhome_1 -l listener3 "
            echo "IF U want kown which resources already set in auto-start"
            echo "sh DbServiceSet.sh -m l"
            echo ""
            echo "!!!ATTENTION:"
            echo "If U want run the script to add resource(s) auto-start MUST be with -o and [-l or -d]"
            echo ""
            echo ""
            exit 1
            ;;
        l)
            LISTENER_NAMES=$OPTARG
            echo "option:l, value $OPTARG"
            echo "LISTENER_NAMES IS: $LISTENER_NAMES"
            ;;
        m)
            MODE_FLAG=$OPTARG
            echo "option:m, value $OPTARG"
            echo "MODE_FLAG IS: $MODE_FLAG" 
            ;;            
        o)
            ORA_HOME=$OPTARG
            echo "option:o, value $OPTARG"
            echo "ORA_HOME IS: $ORA_HOME"
            ;;
        \?)
            echo "Warnning: Please must specify -help option and must specify Any option value"
            exit 1
            ;;
    esac
done


function alert() {
	echo -e "`date` $1"
	exit -1
}


DATE_STR=`date +%Y-%m-%d`
OS_VERSION=`cat /etc/redhat-release|tr -cd 0-9.|awk -F "." '{print $1}'` 
SCRIPTS_DIR=/tmp/McScripts
BAK_DIR=${SCRIPTS_DIR}/McInstallBak_${DATE_STR}
PRO_DIR=${SCRIPTS_DIR}/McInstallPro_${DATE_STR}
LOG_DIR=${SCRIPTS_DIR}/McInstallLog_${DATE_STR}
ROLLBAK_SCRIPT=/tmp/mc_os_rollbak.sh

if [ -e $ROLLBAK_SCRIPT ]; then
    mv $ROLLBAK_SCRIPT ${ROLLBAK_SCRIPT}_`date +%Y-%m-%d_%H%M`
    touch $ROLLBAK_SCRIPT
fi
mkdir -p  ${BAK_DIR} ${PRO_DIR} ${LOG_DIR}
chmod -R 777 ${BAK_DIR} ${PRO_DIR} ${LOG_DIR}

#file_backup /etc/hosts ${BAK_DIR} ${ROLLBAK_SCRIPT}
function file_backup() {
   local target_file=$1  
   local backup_dir=$2 
   local rollback_script=$3
   test -z "$rollback_script" && rollback_script=N
   DATE_STR=`date +%Y%m%d%H%M`
   file_dir=$(dirname ${target_file})
   file_name=$(basename ${target_file})
   if [ -e ${target_file} ]; then
       cp -p ${target_file} ${backup_dir}
       cp -p ${target_file} ${backup_dir}/${file_name}.${DATE_STR}
       if [ $rollback_script = 'N' ]; then
           echo "the rollback_script is NULL;"
           echo " the ${target_file} is not add to rollback_script!"
       else
           test -e ${rollback_script} || touch ${rollback_script}
           row_count=$(grep ${file_name} ${rollback_script}|wc -l)  
           if [ ${row_count} -eq 0 ]; then
               cat >>${rollback_script} <<EOF
cp -f ${backup_dir}/${file_name}  ${file_dir}
EOF
           fi
       fi
   else
       echo "${file_name} not exsit"
   fi
}


#run the function by oracle RDBMS owner
function get_infos() {
    get_sqlplus_count=$(find / -name sqlplus 2>/dev/null |grep "bin/sqlplus"|wc -l 2>/dev/null) 
    #echo ${get_sqlplus_count}
    get_sqlplus_dirs=$(find / -name sqlplus 2>/dev/null |grep "bin/sqlplus"  2>/dev/null)
    #echo ${get_sqlplus_dirs}
    if [ $get_sqlplus_count -gt 1 ]; then
       for i in ${get_sqlplus_dirs}; 
       do
           sqlplus_bin_dir=$(dirname ${i}) 
           ora_home=$(dirname ${sqlplus_bin_dir})
           echo "ORACLE_HOME is: " ${ora_home}
           ora_user=$(getfacl -p ${i}|grep owner|awk '{print $3}')
           echo "the ORACLE_HOME owner is: " ${ora_user}
           lsnr_count=$( ps -ef|grep "${sqlplus_bin_dir}/tnslsnr" |grep -v grep|wc -l)
           lsnr_list=$(ps -ef|grep "${sqlplus_bin_dir}/tnslsnr"|grep -v grep|awk '{print $9 }'|sed ':a;N;$!ba;s/\n/,/g') #listener1,listener2
           echo "the ORACLE_HOME have ${lsnr_count} listener(s) :${lsnr_list} "
           db_count=$(grep ${ora_home}   /etc/oratab |grep -v '^#' |awk -F':' '{print $1}'|wc -l)
           db_names=$(grep ${ora_home}   /etc/oratab |grep -v '^#' |awk -F':' '{print $1}'|grep -v '^#' |sed ':a;N;$!ba;s/\n/,/g')
           echo  "the ORACLE_HOME have ${db_count} database(s): " ${db_names}
 
       done 
    else
        sqlplus_bin_dir=$(dirname ${get_sqlplus_dirs}) 
        ora_home=$(cd ${sqlplus_bin_dir}/..;pwd)
        echo "ORACLE_HOME is: " ${ora_home}
        ora_user=$(getfacl -p ${get_sqlplus_dirs}|grep owner|awk '{print $3}')
        echo "ORACLE_HOME owner is: " ${ora_user}
        lsnr_count=$( ps -ef|grep "${sqlplus_bin_dir}/tnslsnr" |grep -v grep|wc -l)
        lsnr_list=$(ps -ef|grep "${sqlplus_bin_dir}/tnslsnr"|grep -v grep|awk '{print $9 }'|sed ':a;N;$!ba;s/\n/,/g') #listener1,listener2
        echo "the ORACLE_HOME have ${lsnr_count} running listener(s) :${lsnr_list} " 
        db_count=$(grep ${ora_home}   /etc/oratab |grep -v '^#' |awk -F':' '{print $1}'|wc -l)
        db_names=$(grep ${ora_home}   /etc/oratab |grep -v '^#' |awk -F':' '{print $1}'|grep -v '^#' sed ':a;N;$!ba;s/\n/,/g')
        echo  "the ORACLE_HOME have ${db_count} running database(s): " ${db_names}
    fi
              
}

function gather_lis_infos() {
    i_lsnr_count=$(echo ${LISTENER_NAMES}|grep -c ',') #judge listener more than 2
    if [ $i_lsnr_count -ge 1 ]; then
        for j in $(echo $LISTENER_NAMES | sed 's/,/ /g');
        do
            echo "su - ${ORA_USER} -c \"cd ${ORA_HOME}/bin; lsnrctl start ${j} \" ">>${PRO_DIR}/startResources.sh
            echo "su - ${ORA_USER} -c \"cd ${ORA_HOME}/bin; lsnrctl stop ${j} \" ">>${PRO_DIR}/stopResources.sh
        done
    else
        echo "su - ${ORA_USER} -c \"cd ${ORA_HOME}/bin; lsnrctl start ${LISTENER_NAMES} \" " >>${PRO_DIR}/startResources.sh
        echo "su - ${ORA_USER} -c \"cd ${ORA_HOME}/bin; lsnrctl stop ${LISTENER_NAMES} \" ">>${PRO_DIR}/stopResources.sh
    fi  

}

function gather_db_infos() {
    i_db_count=$(echo $DBNAMES|grep -c ',') #judge database more than 2
    if [ $i_db_count -ge 1 ]; then
        for k in $(echo $DBNAMES | sed 's/,/ /g');
        do
           del_linenum=$(grep -n  "${k}:{ORA_HOME}:N" /etc/oratab|awk -F':' '{print $1}')
           sed -i "${del_linenum}d"  /etc/oratab           
           echo "${k}:${ORA_HOME}:Y" >>/etc/oratab
           echo "su - ${ORA_USER} -c \"sh ${ORA_HOME}/bin/dbstart ${ORA_HOME} \" ">>${PRO_DIR}/startResources.sh
           echo "su - ${ORA_USER} -c \"sh ${ORA_HOME}/bin/dbshut ${ORA_HOME}  \" ">>${PRO_DIR}/stopResources.sh
           #echo "in db for blocks"
        done
    else
        del_linenum=$(grep -n  "${DBNAMES}:{ORA_HOME}:N" /etc/oratab|awk -F':' '{print $1}')
        sed -i "${del_linenum}d" /etc/oratab  
        echo "${DBNAMES}:${ORA_HOME}:Y" >>/etc/oratab
        echo "su - ${ORA_USER} -c \"sh ${ORA_HOME}/bin/dbstart ${ORA_HOME}\" ">>${PRO_DIR}/startResources.sh
        echo "su - ${ORA_USER} -c \"sh ${ORA_HOME}/bin/dbshut ${ORA_HOME}\" ">>${PRO_DIR}/stopResources.sh
        #echo "in db else"
    fi 
}
 
function gather_infos() {
    file_backup ${ORA_HOME}/bin/dbstart ${BAK_DIR}/ ${ROLLBAK_SCRIPT}
    file_backup /etc/oratab ${BAK_DIR}/ ${ROLLBAK_SCRIPT}
    file_backup /home/oracle/startDbService.sh  ${BAK_DIR}/  
    file_backup /home/oracle/stopDbService.sh  ${BAK_DIR}/ 
    ORA_USER=$(getfacl -p ${ORA_HOME}|grep owner|awk '{print $3}')
    test -z ${LISTENER_NAMES} || gather_lis_infos
    test -z ${DBNAMES} || gather_db_infos 
    chmod +x ${PRO_DIR}/startResources.sh ${PRO_DIR}/stopResources.sh 
}

function list_start_info() {
     test -e /etc/rc.d/init.d/DbService || echo "No Resource[database|listener] set auto-start"
     echo "auto-start resource list:"
     db_infos=$(grep ':Y$' /etc/oratab |grep -v '^#' ) #|awk -F':' '{print "database name: " $1 "\noracle home: " $2 "\nhome owner: " }' 
     for d in ${db_infos} ;
     do 
         echo $d |awk -F':' '{print "database name: " $1 "\noracle home: " $2 }' 
         db_home=$(echo $d|awk -F':' '{print $2}' ) 
         ORA_USER=$(getfacl -p ${db_home}|grep owner|awk '{print $3}') 
         echo "the ORACLE_HOME owner is: " ${ORA_USER}
     done 
     lis_info=$( grep "lsnrctl start" /home/oracle/startDbService.sh |awk '{print $6 "," $9 }')
     for l in ${lis_info};
     do
         tmp_db_home=$(echo $l |awk -F',' '{print $1}')
         lis_db_home=${tmp_db_home%/*}
         echo $l|awk -F',' '{print "listener name: " $2 }'
         echo "listener home: " $lis_db_home
         ORA_USER=$(getfacl -p ${lis_db_home}|grep owner|awk '{print $3}')
         echo "the ORACLE_HOME owner is: " ${ORA_USER}
     done
}

function set_infos() {
    >${PRO_DIR}/startResources.sh
    >${PRO_DIR}/stopResources.sh
    gather_infos
    cat ${PRO_DIR}/startResources.sh >> /home/oracle/startDbService.sh 
    cat ${PRO_DIR}/stopResources.sh >>/home/oracle/stopDbService.sh
    chown root:root /home/oracle/startDbService.sh
    chown root:root /home/oracle/stopDbService.sh
    chmod +x /home/oracle/startDbService.sh
    chmod +x /home/oracle/stopDbService.sh
}

function setOSService() { 
cat >${PRO_DIR}/DbService<<EOF
#!/bin/bash
#chkconfig: 2345 80 90
#description:DbService
StartDbService(){
    sleep 2
    echo "start DbService..."
    /home/${ORA_USER}/startDbService.sh
}
 
 
StopDbService(){
    sleep 2
    echo "stop DbService..."
    /home/${ORA_USER}/stopDbService.sh
}
  
 
case \$1 in
start)
      StartDbService
      ;;
stop)
      StopDbService
      ;;
restart)
      StopDbService
      StartDbService
      ;;
*)
      echo "Usage: DbService {start|stop|restart}"
      exit 1
      ;;
esac
EOF

    cp ${PRO_DIR}/DbService /etc/rc.d/init.d/DbService
    chmod 755 /etc/rc.d/init.d/DbService 
    chkconfig --add DbService
    chkconfig DbService on 
    test $? != 0 && alert "ERROR:setOSService had failed!!"
}




function main {
	  DEBUG_FLG='McDeBuG'
	  my_debug_flg=`echo $*| awk '{print $NF}'`
    if [[ "$my_debug_flg" = "$DEBUG_FLG" ]]; then
        export PS4='+{$LINENO:${FUNCNAME[0]}} '
        set -x
        echo args=$@
    fi
    if [ -z "$MODE_FLAG" ];then
        [ -n "$ORA_HOME" ] && [ -n "$DBNAMES" -o -n "$LISTENER_NAMES" ] && MODE_FLAG=s || MODE_FLAG=g 
    fi 
    case $MODE_FLAG in
    [gG])
         echo "-----------------------INFO:DbServiceSET's get_infos function begin -----------------------";date
         get_infos
         echo "-----------------------INFO:DbServiceSET's get_infos function end -----------------------";date
         ;;
    [lL])
         echo "-----------------------INFO:DbServiceSET's list_start_info function begin -----------------------";date
         list_start_info
         echo "-----------------------INFO:DbServiceSET's list_start_info function end -----------------------";date         
         ;;
    [sS])
         test -z "$ORA_HOME" && alert "U need run the script to add resource auto-start with -o and [-l or -d] "
         echo "-----------------------INFO:DbServiceSET's set_infos function begin -----------------------";date
         set_infos
         echo "-----------------------INFO:DbServiceSET's set_infos function end -----------------------";date
         [ -e /etc/rc.d/init.d/DbService ] && echo "-----------------------INFO:Resource set finished -----------------------" `date`;
         echo "-----------------------INFO:DbServiceSET's setOSService function begin -----------------------";date
         setOSService
         echo "-----------------------INFO:DbServiceSET's setOSService function end -----------------------";date
         echo "-----------------------INFO:Resource set finished -----------------------";date
         ;; 
    esac

    
}

main $@ 2>&1 