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


![Product Name Screen Shot](img/dashboard.png)


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
   API: http://0.0.0.0:5000/docs
   DASHBOARD: http://0.0.0.0:5000/
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
   API: http://0.0.0.0:8000/docs
   DASHBOARD: http://0.0.0.0:5000/
   ```
<!-- USAGE EXAMPLES -->
## Usage
1. Sign-in to [DASHBOARD:](http://0.0.0.0:5000/)

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

<!-- ROADMAP -->
## Roadmap

* Download deployment in local ( include terraform plan variables, and remote state code)
* Add plan button in Dashboard
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
