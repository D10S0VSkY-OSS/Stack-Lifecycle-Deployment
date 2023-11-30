import logging
import subprocess
import redis
from config.api import settings

redis_client = redis.Redis(host=settings.CACHE_SERVER, port=6379, db=15)


def command(command: str, channel: str):
    try:
        output_lines = []
        command_description = f"Executing command: {command}"
        output_lines.append("-" * 80)
        output_lines.append(command_description)
        output_lines.append("-" * 80)
        redis_client.publish(channel, "-" * 80)
        redis_client.publish(channel, command_description)
        redis_client.publish(channel, "-" * 80)

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        logging.info("#" * 80)
        for line in process.stdout:
            if "[DEBUG]" not in line:
                cleaned_line = line.strip()
                output_lines.append(cleaned_line)
                logging.info(cleaned_line)
                try:
                    redis_client.publish(f'{channel}', cleaned_line)
                except Exception as err:
                    logging.error(f"Error publish redis: {err}")

        logging.info("#" * 80)

        process.wait()

        if process.returncode == 0:
            logging.info(f"Command {command} executed successfully.")
        else:
            logging.error(
                f"Error executing the command {command}. Exit code: {process.returncode}"
            )
        return process.returncode, output_lines
    except subprocess.CalledProcessError as err:
        logging.error(
            f"Error execute command code: {err.returncode}. Error:\n{err.stderr}"
        )
        return err.returncode, err.stderr
