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
    docker-compose up -d  db redis
    sleep 15
}


start_backend() {
    docker-compose up -d --remove-orphan api-backend worker remote-state
    sleep 10
}


start_frontend() {
    docker-compose up -d --remove-orphan sld-dashboard schedule
}


start_init_credentials() {
    curl -X POST "http://localhost:8000/api/v1/users/start" \
        -H  "accept: application/json" \
        -H  "Content-Type: application/json" \
        -d "{\"password\":\"Password08@\"}" \
        -s -o /dev/null

    token=$(curl -X POST \
        -s "http://localhost:8000/api/v1/authenticate/access-token-json" \
        -H  "accept: application/json" \
        -H  "Content-Type: application/json" \
        -d "{\"username\":\"admin\",\"password\":\"Password08@\"}"|jq .access_token|tr -d '"')

    curl -X POST "http://localhost:8000/api/v1/users/" \
        -H  "accept: application/json" \
        -H  "Authorization: Bearer ${token}" \
        -H  "Content-Type: application/json" \
        -d "{\"username\":\"schedule\",\"fullname\":\"schedule bot\",\"password\":\"Schedule1@local\",\"email\":\"schedule@example.com\",\"privilege\":true,\"is_active\":true,\"master\":true,\"squad\":\"bot\"}" \
        -s -o /dev/null
            echo '#################################################'
            echo '#  Now, you can play with SLD 🕹️                #'
            echo '#################################################'
            echo "API: http://localhost:8000/docs"
            echo "DASHBOARD: http://localhost:5000/"
            echo '---------------------------------------------'
            echo "username: admin"
            echo "password: Password08@"
            echo '---------------------------------------------'
        }
    # Check requirement
    check_docker

    echo
    if [ -z "$*" ];then
        echo "Use: start | stop | logs | list | init"
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

            init)   echo "init SLD"
                start_init_credentials
                ;;


            *)  echo "Option $1 not recognized"
                echo ""
                echo "Use: start | stop | logs | list "
                ;;

            esac

            shift

        done
