import os

ROOT = "www"


def valid_path(path: str) -> bool:
    return os.path.isfile(ROOT + path)
