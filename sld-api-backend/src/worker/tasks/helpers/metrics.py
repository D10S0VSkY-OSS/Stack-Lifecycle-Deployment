import functools
import logging
import sys
from datetime import datetime

# Log set
root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


def push_metric():
    def metric_time(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            data = func(*args, **kwargs)
            end_time = datetime.now()
            delta_time = end_time - start_time
            json_body = {
                "measurement": "elapsed_time",
                "tags": {
                    "function": func.__name__,
                },
                "time": end_time.isoformat(),
                "fields": {"duration": delta_time.total_seconds()},
            }
            try:
                logging.info(f"Task {func.__name__} duration: {delta_time}")
                # logging.info(json_body)
                return data
            except Exception as err:
                logging.error(err)

        return wrapper

    return metric_time
