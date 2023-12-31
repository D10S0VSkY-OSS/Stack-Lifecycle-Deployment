import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVER: str = "http://localhost"
    PORT: str = "8000"
    API: str = "/api/v1"
    USER_SCHEDULE: str = "schedule"
    USER_SCHEDULEC: str = "Schedule1@local"
    USER_ADM: str = "admin"
    PASS_ADM: str = "Password08@"
    USER_TEST: str = "user_test"
    USER_01: str = "user01"
    USER_02: str = "user02"
    USER_OFF: str = "user_off"
    USER_PRIV: str = "admin_squad"
    PASS_USER: str = "Password08@"
    STACK_NAME_AWS: str = "aws_vpc"
    STACK_NAME_GCP: str = "gcp_vpc"
    STACK_NAME_AZURE: str = "azure_vnet01"
    GIT_REPO_AWS: str = "https://gitlab.com/hernand/aws_vpc_tf.git"
    GIT_REPO_GCP: str = "https://gitlab.com/hernand/aws_gcloud_tf.git"
    GIT_REPO_AZURE: str = "https://gitlab.com/hernand/azure_vpc_tf.git"
    INIT_CREDENTIALS: dict = {"password": PASS_ADM}
    CREDENTIALS_ADM: dict = {"username": USER_ADM, "password": PASS_ADM}
    CREDENTIALS_ADM_SQUAD: dict = {"username": USER_PRIV, "password": PASS_USER}
    CREDENTIALS_BAD_PASSWD: dict = {"username": USER_ADM, "password": "bad_password"}
    CREDENTIALS_USER: dict = {"username": USER_01, "password": PASS_USER}
    USER_PATCH: dict = {
        "username": "",
        "fullname": "",
        "password": PASS_ADM,
        "email": "admin@example.com",
        "role": ["yoda"],
        "squad": ["*"],
        "is_active": True,
    }
    USER_POST: dict = {
        "username": USER_TEST,
        "fullname": "test user",
        "password": PASS_USER,
        "email": "test01@example.com",
        "role": ["stormtrooper", "R2-D2"],
        "squad": ["squad1"],
        "is_active": True,
    }
    USER_POST_SQUAD1: dict = {
        "username": USER_01,
        "fullname": "user01",
        "password": PASS_USER,
        "email": "user01@example.com",
        "role": ["stormtrooper"],
        "squad": ["squad1"],
        "is_active": True,
    }
    USER_POST_SQUAD2: dict = {
        "username": USER_02,
        "fullname": "user02",
        "password": PASS_USER,
        "email": "user02@example.com",
        "role": ["stormtrooper"],
        "squad": ["squad2"],
        "is_active": True,
    }
    USER_POST_PRIV: dict = {
        "username": USER_PRIV,
        "fullname": "admin by squad",
        "password": PASS_USER,
        "email": "admin_squad@example.com",
        "role": ["darth_vader"],
        "squad": ["squad1", "squad2"],
        "is_active": True,
    }
    USER_POST_OFF: dict = {
        "username": USER_OFF,
        "fullname": "user disable",
        "password": "Password06@",
        "email": "user_off@example.com",
        "role": ["darth_vader"],
        "squad": ["squad1"],
        "is_active": False,
    }
    USER_SCHEDULE: dict = {
        "username": USER_SCHEDULE,
        "fullname": "bot schedule user",
        "password": USER_SCHEDULEC,
        "email": "schedule@example.com",
        "role": ["yoda", "R2-D2"],
        "squad": ["*"],
        "is_active": True,
    }
    STACK_POST_AWS: dict = {
        "stack_name": STACK_NAME_AWS,
        "git_repo": GIT_REPO_AWS,
        "squad_access": ["*"],
        "branch": "master",
        "description": STACK_NAME_AWS,
        "tf_version": "1.0.7",
    }
    STACK_POST_GCP: dict = {
        "stack_name": STACK_NAME_GCP,
        "git_repo": GIT_REPO_GCP,
        "branch": "master",
        "squad_access": ["*"],
        "description": STACK_NAME_GCP,
        "tf_version": "0.14.1",
    }
    STACK_POST_AZURE: dict = {
        "stack_name": STACK_NAME_AZURE,
        "git_repo": GIT_REPO_AZURE,
        "squad_access": ["*"],
        "branch": "master",
        "description": STACK_NAME_AZURE,
        "tf_version": "1.2.3",
    }
    AWS_TEST_ACCOUNT: dict = {
        "squad": "squad1",
        "environment": "develop",
        "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "default_region": "eu-west-1",
        "extra_variables": {"TF_VAR_aws_account_id": "1234567890", "TF_VAR_aws_secret": "1234"},
    }
    AWS_TEST_ACCOUNT_PRO: dict = {
        "squad": "squad1",
        "environment": "pro",
        "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "default_region": "eu-west-1",
        "role_arn": "arn:aws:iam::1234567890:role/role_name",
        "extra_variables": {"TF_VAR_aws_account_id": "1234567890", "TF_VAR_aws_secret": "1234"},
    }
    AWS_TEST_ACCOUNT_SQUAD2: dict = {
        "squad": "squad2",
        "environment": "develop",
        "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "default_region": "eu-west-1",
        "role_arn": "arn:aws:iam::1234567890:role/role_name",
        "extra_variables": {"TF_VAR_aws_account_id": "1234567890", "TF_VAR_aws_secret": "1234", "TF_VAR_db_password": "1234"},
    }
    AWS_TEST_ACCOUNT_SQUAD2_PRO: dict = {
        "squad": "squad2",
        "environment": "pro",
        "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "default_region": "eu-west-1",
        "profile_name": "string",
        "source_profile": "string",
    }
    DEPLOY_URI: str = "?tf_ver=1.0.7"
    DEPLOY_VARS: dict = {
        "name": "aws_vpc_darth_vader",
        "stack_name": "aws_vpc",
        "squad": "squad1",
        "environment": "develop",
        "start_time": "30 9 * * 1-5",
        "destroy_time": "30 17 * * 1-5",
        "variables": {
            "region": "eu-west-1",
            "vpc_cidr": "19.0.0.0/16",
            "subnet_cidr": {
                "be1": "19.0.0.0/24",
                "be2": "19.0.1.0/24",
                "fe1": "19.0.2.0/24",
                "fe2": "19.0.3.0/24",
            },
            "availability_zone_names": ["eu-west-1"],
            "docker_ports": [{"internal": 8999, "external": 1111, "protocol": "udp"}],
            "password": "PassWW",
        },
    }
    DEPLOY_VARS_USER: dict = {
        "name": "aws_vpc_stormtrooper",
        "stack_name": "aws_vpc",
        "environment": "develop",
        "squad": "squad1",
        "start_time": "30 9 * * 1-5",
        "destroy_time": "30 17 * * 1-5",
        "variables": {
            "region": "eu-west-1",
            "vpc_cidr": "19.0.0.0/16",
            "subnet_cidr": {
                "be1": "19.0.0.0/24",
                "be2": "19.0.1.0/24",
                "fe1": "19.0.2.0/24",
                "fe2": "19.0.3.0/24",
            },
            "availability_zone_names": ["eu-west-1"],
            "docker_ports": [{"internal": 8999, "external": 1111, "protocol": "udp"}],
            "password": "Password",
        },
    }
    DEPLOY_VARS_MASTER: dict = {
        "name": "aws_vpc_yoda",
        "squad": "squad1",
        "stack_name": "aws_vpc",
        "environment": "develop",
        "start_time": "*/5 * * * *",
        "destroy_time": "*/7 * * * *",
        "variables": {
            "vpc_cidr": "11.0.0.0/16",
            "subnet_cidr": {
                "be1": "11.0.0.0/24",
                "be2": "11.0.1.0/24",
                "fe1": "11.0.2.0/24",
                "fe2": "11.0.3.0/24",
            },
            "availability_zone_names": ["eu-west-1"],
            "docker_ports": [{"internal": 8300, "external": 8300, "protocol": "tcp"}],
            "password": "PasswordAdmin",
        },
    }
    DEPLOY_VARS_UPDATE: dict = {
        "name": "aws_vpc_yoda",
        "squad": "squad1",
        "stack_name": "aws_vpc",
        "environment": "develop",
        "start_time": "*/5 * * * *",
        "destroy_time": "*/7 * * * *",
        "variables": {
            "vpc_cidr": "11.0.0.0/16",
            "subnet_cidr": {
                "be1": "11.0.0.0/24",
                "be2": "11.0.1.0/24",
                "fe1": "11.0.2.0/24",
                "fe2": "11.0.3.0/24",
            },
            "availability_zone_names": ["eu-west-1"],
            "docker_ports": [{"internal": 8300, "external": 8300, "protocol": "tcp"}],
            "password": "Pass123",
        },
    }


settings = Settings()
