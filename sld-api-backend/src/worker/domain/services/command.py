import logging
import subprocess
from subprocess import Popen, PIPE
from typing import Tuple, List


class SubprocessHandler:
    def run_command(self, command: str) -> Tuple[int, List[str], List[str]]:
        try:
            process = Popen(
                command,
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True
            )

            stdout_lines, stderr_lines = process.communicate()

            output_lines = stdout_lines.strip().split('\n') if stdout_lines else []
            error_lines = stderr_lines.strip().split('\n') if stderr_lines else []

            if process.returncode == 0:
                return process.returncode, output_lines
            return process.returncode, error_lines

        except subprocess.CalledProcessError as err:
            logging.error(
                f"Error executing command, code: {err.returncode}. Error:\n{err.output}"
            )
            return err.returncode, [], [err.output]

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return 1, [], [str(e)]
