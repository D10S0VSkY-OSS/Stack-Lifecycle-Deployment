import os
import ast
import json
import logging
import configparser

from config.api import settings


def createLocalFolder(dir_path: str):
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass
    except Exception:
        raise


def aws_config(secreto):
    try:
        config = configparser.ConfigParser(strict=False)
        # Check if pass me profile
        if secreto.get('data')['profile_name']:
            # Create folder in home user
            createLocalFolder(settings.AWS_CONGIG_DEFAULT_FOLDER)
            # Read config
            config.read(settings.AWS_SHARED_CONFIG_FILE)
            profile_name = secreto.get('data')['profile_name']
            if not config.has_section(f'profile {profile_name}'):
                config.add_section(f'profile {profile_name}')
            config.set(f'profile {profile_name}', 'role_arn', secreto.get(
                'data')['role_arn'])
            config.set(f'profile {profile_name}', 'region', secreto.get(
                'data')['default_region'])
            config.set(f'profile {profile_name}', 'source_profile', secreto.get(
                'data')['source_profile'])
            with open(settings.AWS_SHARED_CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
                logging.info(
                    f"create config {profile_name} in {settings.AWS_SHARED_CONFIG_FILE} done")
            del secreto
            del profile_name
            del configfile
            del config
            return True
    except Exception as err:
        return False
        logging.warning(err)


def aws_credentials(secreto):
    try:
        config = configparser.ConfigParser(strict=False)
        if secreto.get('data')['source_profile']:
            config.read(settings.AWS_SHARED_CREDENTIALS_FILE)
            source_profile = secreto.get('data')['source_profile']
            if not config.has_section(source_profile):
                config.add_section(source_profile)
            config.set(source_profile, 'region',
                       secreto.get('data')['default_region'])
            config.set(source_profile, 'aws_access_key_id',
                       secreto.get("data")["access_key"])
            config.set(source_profile, 'aws_secret_access_key',
                       secreto.get("data")["secret_access_key"])
            with open(settings.AWS_SHARED_CREDENTIALS_FILE, 'w') as credentialsfile:
                config.write(credentialsfile)
                logging.info(
                    f"create credentials {source_profile} in {settings.AWS_SHARED_CREDENTIALS_FILE} done")
            del secreto
            del source_profile
            del credentialsfile
            del config
            return True
    except Exception as err:
        return False
        logging.warning(err)


def fe_config(secreto):
    try:
        config = configparser.ConfigParser(strict=False)
        # Check if pass me profile
        if secreto.get('data')['profile_name']:
            # Create folder in home user
            createLocalFolder(settings.FE_CONGIG_DEFAULT_FOLDER)
            # Read config
            config.read(settings.FE_SHARED_CONFIG_FILE)
            profile_name = secreto.get('data')['profile_name']
            if not config.has_section(f'profile {profile_name}'):
                config.add_section(f'profile {profile_name}')
            config.set(f'profile {profile_name}', 'role_arn', secreto.get(
                'data')['role_arn'])
            config.set(f'profile {profile_name}', 'region', secreto.get(
                'data')['default_region'])
            config.set(f'profile {profile_name}', 'source_profile', secreto.get(
                'data')['source_profile'])
            with open(settings.FE_SHARED_CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
                logging.info(
                    f"create config {profile_name} in {settings.FE_SHARED_CONFIG_FILE} done")
            del secreto
            del profile_name
            del configfile
            del config
            return True
    except Exception as err:
        return False
        logging.warning(err)

def fe_credentials(secreto):
    try:
        config = configparser.ConfigParser(strict=False)
        if secreto.get('data')['source_profile']:
            config.read(settings.FE_SHARED_CREDENTIALS_FILE)
            source_profile = secreto.get('data')['source_profile']
            if not config.has_section(source_profile):
                config.add_section(source_profile)
            config.set(source_profile, 'region',
                       secreto.get('data')['default_region'])
            config.set(source_profile, 'os_access_key',
                       secreto.get("data")["access_key"])
            config.set(source_profile, 'fe_secret_access_key',
                       secreto.get("data")["secret_access_key"])
            with open(settings.FE_SHARED_CREDENTIALS_FILE, 'w') as credentialsfile:
                config.write(credentialsfile)
                logging.info(
                    f"create credentials {source_profile} in {settings.FE_SHARED_CREDENTIALS_FILE} done")
            del secreto
            del source_profile
            del credentialsfile
            del config
            return True
    except Exception as err:
        return False
        logging.warning(err)


def secret(
        stack_name,
        environment,
        squad, name,
        secreto,
):
    if any(i in stack_name.lower() for i in settings.AWS_PREFIX):
        try:
            if not aws_config(secreto) or not aws_credentials(secreto):
                os.environ["AWS_ACCESS_KEY_ID"] = secreto.get("data")[
                    "access_key"]
                os.environ["AWS_SECRET_ACCESS_KEY"] = secreto.get("data")[
                    "secret_access_key"]
                logging.info(f"Set aws account without asume role {squad}, {environment}, {stack_name}, {name}")
        except Exception as err:
            logging.warning(err)

    elif any(i in stack_name.lower() for i in settings.FE_PREFIX):
        try:
            if not fe_config(secreto) or not fe_credentials(secreto):
                os.environ["OS_ACCESS_KEY"] = secreto.get("data")[
                    "access_key"]
                os.environ["FE_SECRET_ACCESS_KEY"] = secreto.get("data")[
                    "secret_access_key"]
                logging.info(f"Set fe account without asume role {squad}, {environment}, {stack_name}, {name}")
        except Exception as err:
            logging.warning(err)

    elif any(i in stack_name.lower() for i in settings.GCLOUD_PREFIX):
        gcloud_keyfile = f"/tmp/{stack_name}/{environment}/{squad}/{name}/gcp_{environment}_{stack_name}_{name}.json"
        gcloud_keyfile_data = ast.literal_eval(
            secreto.get("data")["gcloud_keyfile_json"])
        with open(gcloud_keyfile, 'w') as gcloud_file:
            json.dump(gcloud_keyfile_data, gcloud_file, indent=4)

        os.environ["GOOGLE_CLOUD_KEYFILE_JSON"] = gcloud_keyfile

    elif any(i in stack_name.lower() for i in settings.AZURE_PREFIX):
        os.environ["ARM_CLIENT_ID"] = secreto.get("data")["client_id"]
        os.environ["ARM_CLIENT_SECRET"] = secreto.get("data")[
            "client_secret"]
        os.environ["ARM_SUBSCRIPTION_ID"] = secreto.get("data")[
            "subscription_id"]
        os.environ["ARM_TENANT_ID"] = secreto.get("data")["tenant_id"]


def unsecret(stack_name, environment, squad, name, secreto):
    if any(i in stack_name.lower() for i in settings.AWS_PREFIX):
        try:
            if secreto.get('data')['profile_name']:
                config = configparser.ConfigParser(strict=False)
                config.read(settings.AWS_SHARED_CONFIG_FILE)
                profile_name = secreto.get('data')['profile_name']
                config.remove_option(f'profile {profile_name}', 'role_arn')
                config.remove_option(f'profile {profile_name}', 'region')
                config.remove_option(
                    f'profile {profile_name}', 'source_profile')
                config.remove_section(f'profile {profile_name}')
                with open(settings.AWS_SHARED_CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
                logging.info(f"remove config {profile_name} done")
                del config

            if secreto.get('data')['source_profile']:
                config = configparser.ConfigParser(strict=False)
                config.read(settings.AWS_SHARED_CREDENTIALS_FILE)
                source_profile = secreto.get('data')['source_profile']
                config.remove_option(source_profile, 'region')
                config.remove_option(source_profile, 'aws_access_key_id')
                config.remove_option(
                    source_profile, 'aws_secret_access_key')
                config.remove_section(source_profile)
                with open(settings.AWS_SHARED_CREDENTIALS_FILE, 'w') as credentialsfile:
                    config.write(credentialsfile)
                logging.info(f"remove credentials {source_profile} done")
                del config
            else:
                os.environ.pop("AWS_ACCESS_KEY_ID")
                os.environ.pop("AWS_SECRET_ACCESS_KEY")
        except Exception as err:
            logging.warning(err)

    elif any(i in stack_name.lower() for i in settings.FE_PREFIX):
        try:
            if secreto.get('data')['profile_name']:
                config = configparser.ConfigParser(strict=False)
                config.read(settings.FE_SHARED_CONFIG_FILE)
                profile_name = secreto.get('data')['profile_name']
                config.remove_option(f'profile {profile_name}', 'role_arn')
                config.remove_option(f'profile {profile_name}', 'region')
                config.remove_option(
                    f'profile {profile_name}', 'source_profile')
                config.remove_section(f'profile {profile_name}')
                with open(settings.FE_SHARED_CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
                logging.info(f"remove config {profile_name} done")
                del config

            if secreto.get('data')['source_profile']:
                config = configparser.ConfigParser(strict=False)
                config.read(settings.FE_SHARED_CREDENTIALS_FILE)
                source_profile = secreto.get('data')['source_profile']
                config.remove_option(source_profile, 'region')
                config.remove_option(source_profile, 'os_access_key')
                config.remove_option(
                    source_profile, 'fe_secret_access_key')
                config.remove_section(source_profile)
                with open(settings.FE_SHARED_CREDENTIALS_FILE, 'w') as credentialsfile:
                    config.write(credentialsfile)
                logging.info(f"remove credentials {source_profile} done")
                del config
            else:
                os.environ.pop("OS_ACCESS_KEY")
                os.environ.pop("FE_SECRET_ACCESS_KEY")
        except Exception as err:
            logging.warning(err)

    elif any(i in stack_name.lower() for i in settings.GCLOUD_PREFIX):
        os.environ.pop("GOOGLE_CLOUD_KEYFILE_JSON")
    elif any(i in stack_name.lower() for i in settings.AZURE_PREFIX):
        os.environ.pop("ARM_CLIENT_ID")
        os.environ.pop("ARM_CLIENT_SECRET")
        os.environ.pop("ARM_SUBSCRIPTION_ID")
        os.environ.pop("ARM_TENANT_ID")


