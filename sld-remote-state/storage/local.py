import json
import logging
import os

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class Storage(object):
    def __init__(self, path):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def _log(self, id, op, data):
        log_file = os.path.join(self.path, id) + ".log"
        with open(log_file, "a") as f:
            f.write("%s: %s\n" % (op, data))

    def get(self, id):
        file = os.path.join(self.path, id)
        if os.path.exists(file):
            with open(file) as f:
                d = f.read()
                self._log(id, "state_read", {})
                return json.loads(d)
        return None

    def put(self, id, info):
        file = os.path.join(self.path, id)
        data = json.dumps(info, indent=4, sort_keys=True)
        with open(file, "w") as f:
            f.write(data)
            self._log(id, "state_write", data)

    def lock(self, id, info):
        lock_file = os.path.join(self.path, id) + ".lock"
        if os.path.exists(lock_file):
            with open(lock_file) as f:
                l = json.loads(f.read())
            return False, l

        data = json.dumps(info, indent=4, sort_keys=True)
        with open(lock_file, "w") as f:
            f.write(data)
        self._log(id, "lock", data)
        return True, {id}

    def unlock(self, id, info):
        lock_file = os.path.join(self.path, id) + ".lock"
        if os.path.exists(lock_file):
            os.unlink(lock_file)
            self._log(id, "unlock", json.dumps(info, indent=4, sort_keys=True))
            return True
        return False
