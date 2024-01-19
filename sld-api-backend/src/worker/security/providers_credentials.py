import ast
import configparser
import json
import logging
import os
import boto3

from config.api import settings
from src.shared.security.vault import vault_decrypt


@vault_decrypt
def decrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


def export_environment_variables(dictionary):
    if 'extra_variables' in dictionary and isinstance(dictionary['extra_variables'], dict):
        for key, value in dictionary['extra_variables'].items():
            os.environ[key] = decrypt(value)


class SecretsProviders:
    def __init__(self, secret_provider: dict) -> None:
        self.secret_provider = secret_provider

    def export(self):
        for k, v in self.secret_provider.items():
            os.environ[k] = v


def aws_credentials_context(secreto: dict, session_name: str = "sld-worker"):
    try:
        os.environ["AWS_ACCESS_KEY_ID"] = decrypt(secreto.get("access_key_id"))
        os.environ["AWS_SECRET_ACCESS_KEY"] = decrypt(secreto.get("secret_access_key"))
        os.environ["AWS_DEFAULT_REGION"] = secreto.get("default_region")

        if secreto.get("role_arn"):
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=decrypt(secreto.get("access_key_id")),
                aws_secret_access_key=decrypt(secreto.get("secret_access_key")),
            )
            assumed_role = sts_client.assume_role(RoleArn=secreto.get("role_arn"), RoleSessionName=session_name)
            credentials = assumed_role['Credentials']
            os.environ['AWS_ACCESS_KEY_ID'] = credentials['AccessKeyId']
            os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
            os.environ["AWS_DEFAULT_REGION"] = secreto.get("default_region")
            os.environ['AWS_SESSION_TOKEN'] = credentials['SessionToken']
            os.environ["TF_VAR_role_arn"] = secreto.get("role_arn")
    except Exception as err:
        logging.error(err)


def createLocalFolder(dir_path: str):
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass
    except Exception:
        raise


def secret(
    stack_name,
    environment,
    squad,
    name,
    secreto,
):
    if any(i in stack_name.lower() for i in settings.AWS_PREFIX):
        session_name = f"{squad}-{environment}-{name}"
        aws_credentials_context(secreto=secreto, session_name=session_name)

    elif any(i in stack_name.lower() for i in settings.GCLOUD_PREFIX):
        export_environment_variables(secreto)
        gcloud_keyfile = f"/tmp/{stack_name}/{environment}/{squad}/{name}/gcp_{environment}_{stack_name}_{name}.json"
        gcloud_keyfile_data = ast.literal_eval(decrypt(secreto.get("gcloud_keyfile_json")))
        with open(gcloud_keyfile, "w") as gcloud_file:
            json.dump(gcloud_keyfile_data, gcloud_file, indent=4)

        os.environ["GOOGLE_CLOUD_KEYFILE_JSON"] = gcloud_keyfile

    elif any(i in stack_name.lower() for i in settings.AZURE_PREFIX):
        export_environment_variables(secreto)
        os.environ["ARM_CLIENT_ID"] = decrypt(secreto.get("client_id"))
        os.environ["ARM_CLIENT_SECRET"] = decrypt(secreto.get("client_secret"))
        os.environ["ARM_SUBSCRIPTION_ID"] = secreto.get("subscription_id")
        os.environ["ARM_TENANT_ID"] = secreto.get("tenant_id")

    elif any(i in stack_name.lower() for i in settings.CUSTOM_PREFIX):
        configuration = ast.literal_eval(secreto.get("custom_provider_keyfile_json"))
        R = SecretsProviders(configuration)
        R.export()


def unsecret(stack_name, environment, squad, name, secreto):
    if any(i in stack_name.lower() for i in settings.AWS_PREFIX):
        try:
            if secreto.get("profile_name"):
                config = configparser.ConfigParser(strict=False)
                config.read(settings.AWS_SHARED_CONFIG_FILE)
                profile_name = secreto.get("profile_name")
                config.remove_option(f"profile {profile_name}", "role_arn")
                config.remove_option(f"profile {profile_name}", "region")
                config.remove_option(f"profile {profile_name}", "source_profile")
                config.remove_section(f"profile {profile_name}")
                with open(settings.AWS_SHARED_CONFIG_FILE, "w") as configfile:
                    config.write(configfile)
                logging.info("removed config done")
                del config

            if secreto.get("source_profile"):
                config = configparser.ConfigParser(strict=False)
                config.read(settings.AWS_SHARED_CREDENTIALS_FILE)
                source_profile = secreto.get("source_profile")
                config.remove_option(source_profile, "region")
                config.remove_option(source_profile, "aws_access_key_id")
                config.remove_option(source_profile, "aws_secret_access_key")
                config.remove_section(source_profile)
                with open(settings.AWS_SHARED_CREDENTIALS_FILE, "w") as credentialsfile:
                    config.write(credentialsfile)
                logging.info("removed credentials done")
                del config
            else:
                os.environ.pop("AWS_ACCESS_KEY_ID")
                os.environ.pop("AWS_SECRET_ACCESS_KEY")
        except Exception as err:
            logging.warning(err)
    elif any(i in stack_name.lower() for i in settings.GCLOUD_PREFIX):
        os.environ.pop("GOOGLE_CLOUD_KEYFILE_JSON")
    elif any(i in stack_name.lower() for i in settings.AZURE_PREFIX):
        os.environ.pop("ARM_CLIENT_ID")
        os.environ.pop("ARM_CLIENT_SECRET")
        os.environ.pop("ARM_SUBSCRIPTION_ID")
        os.environ.pop("ARM_TENANT_ID")

    elif any(i in stack_name.lower() for i in settings.CUSTOM_PREFIX):
        pass
