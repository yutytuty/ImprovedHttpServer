import os

ROOT = "www"


def valid_path(path: str) -> bool:
    return os.path.isfile(ROOT + path)


def read_file(path: str) -> bytes:
    for root, _, files in os.walk(ROOT):
        for name in files:
            current_path = os.path.join(root, name)
            print(current_path)
            if path == current_path.lstrip("www"):
                with open(current_path, "rb") as f:
                    return f.read()
    return b""
