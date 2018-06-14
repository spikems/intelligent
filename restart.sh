ps aux |grep uwsgi|grep -v grep | awk '{print $2}' |while read d;do kill -9 $d;done
sleep 3
nohup uwsgi --ini uwsgi.ini >log.info 2>&1 &
