# Play with sld on k8s

```bash
./kplay start

./kplay init
```

# Play with sld on k8s + metallb + istio


### 1-Deploy cluster k8s
```
kind create cluster --config kind.yml

```
### 2-Download Istio 
```
curl -L https://istio.io/downloadIstio | sh -
```

### 3-Deploy Istio
```
istio-1.9.1/bin/istioctl install --set profile=demo -y
```

### 4-Deploy Istio with addons
```
kubectl apply -f k8s/istio/addons/
```

### 5-Inyect istio to namespace
```
kubectl label namespace default istio-injection=enabled
```

### 5-Apply SLD
```
kubectl apply -k k8s/ 
```

### 6-Create Istio GW and VirtualService

```
cd k8s/istio

kubectl create \
-n istio-system secret tls sld-dashboard-credential \
--key=sld-dashboard-client.acme.com.key --cert=sld-dashboard.acme.com.crt

kubectl create \
-n istio-system secret tls sld-api-credential \
--key=sld-api-client.acme.com.key --cert=sld-api.acme.com.crt

kubectl apply -f k8s/istio/istio-tls.yaml
```

### 7-Finally Add EXTERNAL-IP in /etc/hosts

```

# kubectl -n istio-system get service istio-ingressgateway
NAME                   TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)                                                                     AGE
istio-ingressgateway   LoadBalancer   10.96.218.227   172.19.255.200  

# Add EXTERNAL-IP in /etc/hosts
172.19.255.200 sld-dashboard.acme.com
172.19.255.200 sld-api.acme.com

# Check Virtual service amd GW
kubectl -n istio-system get service istio-ingressgateway
kubectl get virtualservices
kubectl get gateways
```

```
https://sld-dashboard.acme.com/
https://sld-api.acme.com/docs
```
