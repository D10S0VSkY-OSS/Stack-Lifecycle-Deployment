#!/bin/bash
check_docker () {
/usr/bin/which docker-compose >/dev/null
if [ $? = 0 ];then
    echo "docker-compse ok"
else
    echo "Docker Compose not installed"
    echo "Run this command to download the current stable release of Docker Compose:"
    echo 'sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
    echo 'sudo chmod +x /usr/local/bin/docker-compose'
    exit 1
fi
/usr/bin/which docker > /dev/null
if [ $? = 0 ];then
    echo "docker ok"
else
    echo "Docker not installed"
    echo "The installation of dokcer is a requirement:"
    echo 'https://docs.docker.com/engine/install/ubuntu/'
    exit 1
fi
}


start_db_redis_rabbit() {
    docker-compose up -d  db redis rabbit
    sleep 15
}
start_backend() {
    docker-compose up -d --remove-orphan api-backend worker remote-state
    sleep 10
}

start_frontend() {
    docker-compose up -d --remove-orphan sld-dashboard schedule
}
# Check requirement 
check_docker

echo
if [ -z "$*" ];then
    echo "Use: start | stop | logs | list "
fi
while [ -n "$1" ]; do # while loop starts

	case "$1" in

	start)  echo "Starting SLD for play" 
            start_db_redis_rabbit
            start_backend
            start_frontend 
            ;; 

	stop)   echo "Stoping SLD for play"
            docker-compose down
            ;;

	logs)   echo "CRL+C for escape"
            sleep 3
            docker-compose logs -f 
            ;;

	list)   echo "List endpoints"
            docker-compose ps|awk '{print $1,":", "http://"$7}' |awk -F"-" '{print $2}' |grep dash
            docker-compose ps|awk '{print $1,":", "http://"$8}' |awk -F">" '{print $1}'|sed 's/.$//'|grep api
            ;;


	*)  echo "Option $1 not recognized"
        echo ""
	    echo "Use: start | stop | logs | list "
        ;;

	esac

	shift

done
