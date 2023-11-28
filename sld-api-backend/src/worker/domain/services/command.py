import logging
import subprocess
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=15)


def command(command: str, channel: str):
    try:
        output_lines = []

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        logging.info("#" * 80)
        for line in process.stdout:
            output_lines.append(line.strip())
            logging.info(line.strip())
            try:
                redis_client.publish(f'{channel}', line.strip())
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
        return None
