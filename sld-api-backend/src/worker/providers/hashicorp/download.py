import os
import stat
import zipfile
from io import BytesIO

import requests
from urllib3.exceptions import InsecureRequestWarning
from src.worker.domain.entities.worker import DownloadBinaryParams
import logging
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from config.api import settings


class BinaryDownload():
    def __init__(self, params: DownloadBinaryParams):
        self.iac_type = params.iac_type
        self.version = params.version

    def get(self) -> dict:
        try:
            if self.iac_type == "tofu":
                iac_version = self.version.replace("v", "")
                logging.info(f"Downloading binary iac_type {self.iac_type} version {iac_version}")
                # Download Terraform binary if not already downloaded
                if not os.path.exists(f"/tmp/{self.version}"):
                    os.mkdir(f"/tmp/{self.version}")
                    if not os.path.isfile(f"/tmp/{self.version}/tofu"):
                        binary = f"https://github.com/opentofu/opentofu/releases/download/v{iac_version}/tofu_{iac_version}_linux_amd64.zip"
                        print(binary)
                        req = requests.get(binary, verify=False)
                        _zipfile = zipfile.ZipFile(BytesIO(req.content))
                        _zipfile.extractall(f"/tmp/{self.version}")
                        st = os.stat(f"/tmp/{self.version}/tofu")
                        os.chmod(f"/tmp/{self.version}/tofu", st.st_mode | stat.S_IEXEC)
    
                return {
                    "command": "opentofuDownload",
                    "rc": 0,
                    "stdout": "OpenTofu downloaded and used successfully",
                }
            elif self.iac_type == "terraform":
                iac_version = self.version.replace("v", "")
                logging.info(f"Downloading binary iac_type {self.iac_type} version {iac_version}")
                # Download Terraform binary if not already downloaded
                if not os.path.exists(f"/tmp/{self.version}"):
                    os.mkdir(f"/tmp/{self.version}")
                    if not os.path.isfile(f"/tmp/{self.version}/terraform"):
                        binary = f"{settings.TERRAFORM_BIN_REPO}/{iac_version}/terraform_{iac_version}_linux_amd64.zip"
                        req = requests.get(binary, verify=False)
                        _zipfile = zipfile.ZipFile(BytesIO(req.content))
                        _zipfile.extractall(f"/tmp/{self.version}")
                        st = os.stat(f"/tmp/{self.version}/terraform")
                        os.chmod(f"/tmp/{self.version}/terraform", st.st_mode | stat.S_IEXEC)
    
                return {
                    "command": "binaryDownload",
                    "rc": 0,
                    "stdout": "Download Binary file",
                }
            elif self.iac_type == "terragrunt":
                logging.info(f"Downloading binary iac_type {self.iac_type} version {self.version}")
                binary_directory = f"/tmp/{self.version}"
                downloaded_binary_path = f"{binary_directory}/terragrunt_linux_amd64"
                renamed_binary_path = f"{binary_directory}/terragrunt"
                # Download Terraform binary if not already downloaded
                if not os.path.exists(f"/tmp/{self.version}"):
                    os.mkdir(f"/tmp/{self.version}")
                if not os.path.isfile(f"/tmp/{self.version}/terragrunt"):
                    binary_url = f"https://github.com/gruntwork-io/terragrunt/releases/download/{self.version}/terragrunt_linux_amd64"
                    response = requests.get(binary_url, stream=True, verify=False)
                    with open(downloaded_binary_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=90000000):
                            file.write(chunk)
                    os.chmod(downloaded_binary_path, os.stat(downloaded_binary_path).st_mode | stat.S_IEXEC)
                    os.rename(downloaded_binary_path, renamed_binary_path)

                    #terrform
                    try:
                        if not os.path.isfile(f"/tmp/{self.version}/terraform"):
                            binary_terraform = f"{settings.TERRAFORM_BIN_REPO}/1.6.5/terraform_1.6.5_linux_amd64.zip"
                            req = requests.get(binary_terraform, verify=False)
                            _zipfile = zipfile.ZipFile(BytesIO(req.content))
                            _zipfile.extractall(f"/tmp/{self.version}")
                            st = os.stat(f"/tmp/{self.version}/terraform")
                            os.chmod(f"/tmp/{self.version}/terraform", st.st_mode | stat.S_IEXEC)
                            current_path = os.environ.get('PATH', '')
                            if binary_directory not in current_path.split(os.pathsep):
                                updated_path = current_path + os.pathsep + binary_directory
                            os.environ['PATH'] = updated_path
                    except Exception as err:
                        logging.error(f"Failed to download Terraform binary from {binary_terraform}")
                        raise err

            else:
                logging.error(f"Failed to download Terragrunt binary from {binary_url}")
                return {"command": "binaryDownload", "rc": 1, "stdout": "Failed to download binary file"}
            return {
                "command": "binaryDownload",
                "rc": 0,
                "stdout": "Download Binary file",
            }
        except Exception as err:
            logging.error(f"Error downloading binary {self.iac_type} error: {err}")
            return {"command": self.iac_type + "Download", "rc": 1, "stdout": err}
