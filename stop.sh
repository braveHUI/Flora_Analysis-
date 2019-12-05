ps u -u `whoami` |grep -v -e "sshd" -e "-bash" -e "ps " -e "systemd" |awk 'NR>1 {print $2}' |xargs echo  kill -9 {}  |sh
