[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment">
    <img src="img/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Stack Lifecycle Deployment</h3>

  <p align="center">
    OpenSource solution that defines and manages the complete lifecycle of resources used and provisioned into a cloud!
    <br />
    <a href="https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment"><strong>Explore the docs »</strong></a>
    <br />
    <br />
  </p>
</p>


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-SLD">About SLD</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#custom-settings">Custom settings</a></li>
      <ul>
        <li><a href="#storage-backend">Storage backend</a></li>
        <li><a href="#data-remote-state">Data remote state</a></li>
        <li><a href="#workers">Workers</a></li>
        <li><a href="#users-roles">Users roles</a></li>
      </ul>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
    <li><a href="#built-with">Built With</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About SLD

SLD helps to accelerate deployment, weighting and making IaaC reusable, generating dynamic forms and maintaining different variables in each environment with the same code. With SLD you can schedule infrastructure deployments like its destruction, manage users by roles and separate stacks by squad and environment


[![Everything Is AWESOME](img/dashboard.png)](https://youtu.be/EThXrat-jsQ "Click me for DEMO")


![Product Name Screen Shot](img/api.png)

Main features:
* Fast API async
* Dashboard / UI
* Distributed tasks routing by squad
* Infrastructure as code (IaC) based in terraform code
* Dynamic html form from terraform variables
* Re-deploy infrastructure keeping the above parameters
* Distributed architecture based microservices
* Task decouple and event driven pattern
* Resilient, rollback deployment and retry if failure

SLD is the easy way to use your terrafrom code!






<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

You need docker and docker-compse or kind ( recomended ).
* [Docker](https://docs.docker.com/get-docker/)
* [Docker-compose](https://docs.docker.com/compose/install/)
* [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
* [kubectl](https://kubernetes.io/es/docs/tasks/tools/install-kubectl/)

### Installation

1. Clone the SLD repo
   ```sh
   git clone https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment.git
   ```
2. Deploy SLD in k8s with kind
   ```sh
   cd Stack-Lifecycle-Deployment/play-with-sld/kubernetes 
   sh kplay.sh start
   ```
   Result:
   ```sh
   Starting SLD for play
   Creating cluster "kind" ...
   ✓ Ensuring node image (kindest/node:v1.20.2) 🖼
   ✓ Preparing nodes 📦 📦  
   ✓ Writing configuration 📜 
   ✓ Starting control-plane 🕹️ 
   ✓ Installing CNI 🔌 
   ✓ Installing StorageClass 💾 
   ✓ Joining worker nodes 🚜 
   Set kubectl context to "kind-kind"
   You can now use your cluster with:

   kubectl cluster-info --context kind-kind
      ```

3. Create init user

   ```sh
   sh kplay.sh init
   ```

   Result:

   ```bash
   kind ok
   docker ok
   kubectl ok
   jq ok
   curl ok

   init SLD
   #################################################
   #  Now, you can play with SLD 🕹️                #
   #################################################
   API: http://localhost:5000/docs
   DASHBOARD: http://localhost:5000/
   ---------------------------------------------
   username: admin
   password: Password08@
   ---------------------------------------------

   ```

   List endopints

   ```sh
   sh kplay.sh list
   ```

   Result:

   ```bash
   kind ok
   docker ok
   kubectl ok

   List endpoints
   API: http://localhost:8000/docs
   DASHBOARD: http://localhost:5000/
   ```
<!-- USAGE EXAMPLES -->
## Usage
1. Sign-in to [DASHBOARD:](http://localhost:5000/)

    ![sign-in](img/sign-in.png)
    
    Click the dashboard link:

    ![sign-in](img/welcome.png)

    

2. Add Cloud account


    ![sign-in](img/account.png)

    fill in the form with the required data.
    in our example we will use
    
    * Squad: squad1 
    * Environment: develop
    
    > by default workers are running as squad1 and squad2 for play purpose, but you can change it and scale when you want


    **When you add an account to a provider ( aws, gcp, azure ) one squad is created, you must create a worker for the name of the created squad, if you don't do it the deployment will remain in a "PENDING" state [Read Workers](#workers)**
  
    
    finally add:
    * Access_key_id
    * Secret_access_key
    * Default_region ( default eu-west-1)
    In case you use assume role, fill in the rest of the data.

3. Add terraform module or stack
   
    ![sign-in](img/add_stack.png)

    * Name: Add the name with a valid prefix according to the cloud provider. 
    > Prefixs supported: aws_ , gcp_, azure_
    * git: Add a valid git repository, like github, gitlab, bitbucket, etc. in our case to play we use (https://github.com/D10S0VSkY-OSS/aws_vpc_poc)
    > You can pass user and  password as https://username:password@github.com/aws_vpc
    > For ssh you can pass it as a secret in the deployment to the user sld
    * Branch: Add the branch you want to deploy by default is master
    * Squad Access: Assign who you want to have access to this stack by squad
    > '*' = gives access to all, you can allow access to one or many squads separated by commas: squad1,squad2
    * tf version: indicates the version of terraform required by the module or stack
    > https://releases.hashicorp.com/terraform/
    * Description: Describe the module or stack to help others during implementation. 
  
4. Deploy your first stack!!!
   
   List stacks for deploy
   
   ![sign-in](img/deploy_1.png)
   
   Choose deploy 
   
   ![sign-in](img/deploy_2.png)
   
   SLD will generate a dynamic form based on the stack variables,
   fill in the form and press the Deploy button

   ![sign-in](img/deploy_3.png)

    > Important! assign the same squad and environment that we previously created when adding the account (See Add Cloud account)

    Now, the status of the task will change as the deployment progresses.

   ![sign-in](img/deploy_4.png)

   You can control the implementation life cycle
   ![sign-in](img/deploy_5.png)
   You can destroy, re-implement that SLD will keep the old values ​​or you can also edit those values ​​at will.
   ![sign-in](img/deploy_6.png)
    And finally you can manage the life cycle programmatically, handle the destruction / creation of the infrastructure, a good practice for the savings plan!!!
    ![sign-in](img/schedule.png)
<!-- USAGE EXAMPLES -->

# Custom settings
## Storage backend
SLD uses its own remote backend, so you don't need to configure any backend in terraform.
The following example shows a backend config
```
        terraform {
          backend "http" {
            address = "http://remote-state:8080/terraform_state/aws_vpc-squad1-develop-vpc_core"
            lock_address = "http://remote-state:8080/terraform_lock/aws_vpc-squad1-develop-vpc_core"
            lock_method = "PUT"
            unlock_address = "http://remote-state:8080/terraform_lock/aws_vpc-squad1-develop-vpc_core"
            unlock_method = "DELETE"
          }
        }
        
```
At the moment SLD supports MongoDB, S3 and local backend (for testing purposes only)
To configure MongoDB as a backend, you must pass the following variables as parameters to the remote-state service:
```
# docker-compose.yaml
    environment:                                                                                                     
      SLD_STORE: mongodb                                                                                             
      SLD_MONGODB_URL: "mongodb:27017/"
      MONGODB_USER: admin
      MONGODB_PASSWD: admin
```
```
# k8s yaml
    env:
    - name: SLD_STORE
      value: mongodb
    - name: SLD_MONGODB_URL
      value: "mongodb:27017/"
    - name: MONGODB_USER
      value: admin
    - name: MONGODB_PASSWD
      value: admin
```
To configure S3 you can pass the access and secret keys of aws, in case SLD is running in AWS it is recommended to use roles
```
    env:
    - name: SLD_STORE
      value: "S3"
    - name: SLD_BUCKET
      value: "s3-sld-backend-cloud-tf-state"
    - name: AWS_ACCESS_KEY
      value: ""
    - name: AWS_SECRET_ACCESS_KEY
      value: ""
```
For Azure env you need set the next env
```
          env:                                                                                                                                    
          - name: SLD_STORE
            value: azure
          - name: AZURE_STORAGE_CONNECTION_STRING
            value: "DefaultEndpointsProtocol=https;AccountName=<YOUR ACCOUNT>;AccountKey=<YOUR ACCESS KEY>;EndpointSuffix=core.windows.net"
```
[See azure-storage-configure-connection-string](https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string)

For google cloud storage set:
```
SLD_STORE=gcp
export GOOGLE_APPLICATION_CREDENTIALS="/app/sld-gcp-credentials.json"
```
**Import google service account key to k8s secret**
```
kubectl create secret generic gcp-storage --from-file=~/Downloads/storage.json
```
**Modify sld-remote-state.yml set gcp storage cloud backend and mount secret:**
```
apiVersion: apps/v1                                                                                                                               
kind: Deployment                                                                                                                                  
metadata:                                                                                                                                         
  name: remote-state                                                                                                                              
  labels:                                                                                                                                         
    name: remote-state                                                                                                                            
spec:                                                                                                                                             
  replicas: 1                                                                                                                                     
  selector:                                                                                                                                       
    matchLabels:                                                                                                                                  
      name: remote-state         
  template:                                                                                                                                                                                                        
    metadata:                                                                  
      labels:                                                            
        name: remote-state                                               
    spec:                        
      subdomain: primary                                                                                                                                                                                                                                                        
      containers:                                                                              
        - name: remote-state                                                                   
          image: d10s0vsky/sld-remote-state:latest                                                                     
          volumeMounts:                    
          - name: gcp                                                                                                                                         
            mountPath: "/app/gcp"                                                                                                                                            
            readOnly: true                          
          env:                                      
          - name: SLD_STORE                         
            value: gcp                              
          - name: GOOGLE_APPLICATION_CREDENTIALS                                                                                                                                                                   
            value: "/app/gcp/storage.json"                                                                             
          resources:                                                
            limits:                                                 
              memory: 600Mi                                         
              cpu: 1                                                                                                                                                                                                                                                            
            requests:                                                          
              memory: 300Mi                                                    
              cpu: 500m                                                        
          imagePullPolicy: Always                                              
          command: ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]                                          
          ports:                                                                               
            - containerPort: 8080                                                              
          livenessProbe:                                                                       
            httpGet:                                                                           
              path: /                                                                          
              port: 8080                                                                                                                                                                      
              httpHeaders:                                                                                             
              - name: status                                                                                           
                value: healthy                                                                                         
            initialDelaySeconds: 60                                                                                    
            periodSeconds: 60                                                                                          
      volumes:                                                                                                         
      - name: gcp                                                                                                      
        secret:                                                                                                        
          secretName: gcp-storage                                                    
```

## Data remote state
To be able to use the outputs of other stacks you can configure it as follows
the key alwys is the same like "Task Name"
| stack-name | squad account | env | deploy name |
| :---: | :---: | :---: | :---: |
| aws_vpc | squad1 | develop | vpc_core |
```
data "terraform_remote_state" "vpc_core" {
  backend = "http"
  config = {
    address = "http://remote-state:8080/terraform_state/aws_vpc-squad1-develop-vpc_core"
  }
}
```
Test example:
```
echo "data.terraform_remote_state.vpc_core.outputs"|terraform console
```
## Workers
The workers in sld are responsible for executing the infrastructure deployment. You can use one or more workers for each account or several accounts at the same time. It all depends on the degree of parallelism and segregation that you consider

```
# Example k8s worker for account squad1, change this for each of your accounts
# Stack-Lifecycle-Deployment/play-with-sld/kubernetes/k8s/sld-worker-squad1.yml
# Add replicas for increment paralelism
# Add more squad accounts if you want to group accounts in the same worker:
# command: ["celery", "--app", "tasks.celery_worker", "worker", "--loglevel=info", "-c", "1", "-E", "-Q", "squad1,"another_squad_account"]

apiVersion: apps/v1
kind: Deployment
metadata:
  name: stack-deploy-worker-squad1
  labels:
    name: stack-deploy-worker-squad1
spec:
  replicas: 1 
  selector:
    matchLabels:
      name: stack-deploy-worker-squad1
  template:
    metadata:
      labels:
        name: stack-deploy-worker-squad1
    spec:
      subdomain: primary
      containers:
        - name: stack-deploy-worker-squad1
          image: d10s0vsky/sld-api:latest
          imagePullPolicy: Always
          env:
          - name: TF_WARN_OUTPUT_ERRORS
            value: "1"
          resources:
            limits:
              memory: 600Mi
              cpu: 1
            requests:
              memory: 300Mi
              cpu: 500m
          command: ["celery", "--app", "tasks.celery_worker", "worker", "--loglevel=info", "-c", "1", "-E", "-Q", "squad1"]

```
```
  # Example docker-compose worker for account squad1, change this for each of your accounts
  # Stack-Lifecycle-Deployment/play-with-sld/docker/docker-compose.yml

  worker:
    image: d10s0vsky/sld-api:latest
    entrypoint: ["celery", "--app", "tasks.celery_worker", "worker", "--loglevel=info", "-c", "1", "-E", "-Q", "squad1"]
    environment:
      BROKER_USER: admin
      BROKER_PASSWD: admin
    depends_on:
      - rabbit
      - redis
      - db
      - remote-state
```
## Users roles
SLD has three preconfigured roles for users to easily manage this.
| roles | scope | description |
| :---: | :---: | :---: |
| yoda | global | Global scope, can see all squads and are full admin |
| darth_vader | one or many squad | Limit the scope of the squad, can see the assigned squads and you are a full manager of only those squads |
| stormtrooper | one or many squad  | Limits squad range, can see assigned squads and can only deploy assigned deployment on belong squad |
| R2-D2 | all, one or many squad  | This role is only for identification and must be associated with the previous ones, its use case is for bot users who access the api |

<!-- Architecture -->
## Architecture
![sign-in](img/architecture_v1.png)

<!-- ROADMAP -->
## Roadmap

* LDAP and SSO authentication
* Slack integration
* FluenD / elasticSearch integration
* InfluxDB integration
* Prometheus
* Estimate pricing by stack
* Anomaly detection
* Advance metrics and logs
* Resource size recommendation based on metrics
* Shift Left Security deployment
* Multi tenancy
* Topology graphs 
* Mutal TLS
* Added workers automatically by squad
* Onboarding resources
* Add more cloud and on-prem providers



<!-- CONTRIBUTING -->
## Contributing

Contributions are what makes the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

lafalce.diego@gmail.com

[Stack Lifecycle Deployment](https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* [Img Shields](https://shields.io)
* [Choose an Open Source License](https://choosealicense.com)
* [volt-dashboard](https://github.com/app-generator/tb-volt-dashboard-flask)



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/D10S0VSkY-OSS/Stack-Lifecycle-Deployment?style=for-the-badge
[contributors-url]: https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/D10S0VSkY-OSS/Stack-Lifecycle-Deployment.svg?style=for-the-badge
[forks-url]: https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment/network/members
[stars-shield]: https://img.shields.io/github/stars/D10S0VSkY-OSS/Stack-Lifecycle-Deployment.svg?style=for-the-badge
[stars-url]: https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment/stargazers
[issues-shield]: https://img.shields.io/github/issues/D10S0VSkY-OSS/Stack-Lifecycle-Deployment?style=for-the-badge
[issues-url]: https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment/issues
[license-shield]: https://img.shields.io/badge/licence-MIT-green?style=for-the-badge
[license-url]: https://github.com/D10S0VSkY-OSS/Stack-Lifecycle-Deployment/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://es.linkedin.com/in/diegolafalce
[product-screenshot]: images/screenshot.png

### Built With

* [FastApi](https://github.com/tiangolo/fastapi)
* [volt-dashboard](https://github.com/app-generator/tb-volt-dashboard-flask)
* [Celery](https://github.com/celery/celery)
* [Ansible-runner](https://github.com/ansible/ansible-runner)
* [Terraform](https://github.com/hashicorp/terraform)
* [Bootstrap](https://getbootstrap.com)
