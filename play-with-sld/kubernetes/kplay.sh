#!/bin/bash
check_pkg () {
    /usr/bin/which kind >/dev/null
    if [ $? = 0 ];then
        echo "kind ok"
    else
        echo "kind not installed"
        echo "curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.10.0/kind-linux-amd64"
        echo 'chmod +x ./kind'
        echo 'mv ./kind /some-dir-in-your-PATH/kind'
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
    /usr/bin/which kubectl > /dev/null
    if [ $? = 0 ];then
        echo "kubectl ok"
    else
        echo "kubectl not installed"
        echo "Install and Set Up kubectl:"
        echo "https://kubernetes.io/docs/tasks/tools/install-kubectl/"
        exit 1
    fi
    /usr/bin/which jq > /dev/null
    if [ $? = 0 ];then
        echo "jq ok"
    else
        echo "jq not installed"
        echo "Please install jq:"
        echo "https://stedolan.github.io/jq/download/"
        exit 1
    fi
    /usr/bin/which curl > /dev/null
    if [ $? = 0 ];then
        echo "curl ok"
    else
        echo "curl not installed"
        echo "Please install curl:"
        echo "https://curl.se/download.html"
        exit 1
    fi
}


start_kubernetes() {
    unset KUBECONFIG
    kind create cluster --config kind.yml && \
        kubectl cluster-info --context kind-kind && \
        kubectl apply -k k8s/
    }


start_init_credentials() {
    check_api=$(kubectl get deployments.apps api-backend |tail -n1|awk '{print $4}')
    if [ $check_api -ne 1 ];then
        echo ""
        echo "Please, wait for API deploy ⏳"
        echo ""
        kubectl get deployments.apps api-backend
        exit 1
    fi
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
check_pkg

    echo
    if [ -z "$*" ];then
        echo "Use: start | stop | list "
    fi
    while [ -n "$1" ]; do # while loop starts

        case "$1" in

            start)  echo "Starting SLD for play"
                start_kubernetes > /dev/null
                echo '#################################################'
                echo '#  infrastructure deployed                      #'
                echo '#  starting SLD  ⏳                             #'
                echo '#################################################'
                ;;

            stop)   echo "Stoping SLD for play"
                kind delete cluster
                unset KUBECONFIG
                ;;

            list)   echo "List endpoints"
                echo "API: http://localhost:8000/docs"
                echo "DASHBOARD: http://localhost:5000/"
                ;;

            init)   echo "init SLD"
                start_init_credentials
                ;;


            *)  echo "Option $1 not recognized"
                echo ""
                echo "Use: start | stop | list | init "
                ;;

            esac

            shift

        done
