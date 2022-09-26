import shutil


class Utils:
    """
    Class where methods similar to a helper are added
    """

    def delete_local_folder(dir_path: str) -> dict:
        try:
            shutil.rmtree(dir_path)
        except FileNotFoundError:
            pass
        except OSError:
            raise
