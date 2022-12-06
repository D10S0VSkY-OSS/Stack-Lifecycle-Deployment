import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from os import listdir
from os.path import isfile, join


@dataclass
class StructBase:
    name: str
    stack_name: str
    environment: str
    squad: str


@dataclass
class Artifact(StructBase):
    git_repo: str
    branch: str
    project_path: str

    def get(self):

        try:
            directory = f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/"
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Directory {directory} created successfully")
        except OSError:
            logging.info(f"Directory {directory} can not be created")

        try:
            if os.path.exists(f"{directory}/{self.name}"):
                shutil.rmtree(f"{directory}/{self.name}")

            logging.info(f"Download git repo {self.git_repo} branch {self.branch}")
            os.chdir(directory)

            result = subprocess.run(
                f"git clone --recurse-submodules --branch {self.branch} {self.git_repo} {self.name}",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )

            logging.info(f"Check if variable.tf file exist")

            tfvars_files = [
                f
                for f in listdir(directory)
                if f.endswith(".tfvars") and isfile(join(directory, f))
            ]

            rc = result.returncode
            if rc != 0:
                return {
                    "command": "git",
                    "rc": rc,
                    "tfvars": tfvars_files,
                    "stdout": result.stderr,
                }
            return {
                "command": "git",
                "rc": rc,
                "tfvars": tfvars_files,
                "stdout": result.stdout,
            }
        except Exception as err:
            return {"command": "git", "rc": 1, "tfvars": tfvars_files, "stdout": err}
