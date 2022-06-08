import secrets
from pathlib import Path
from typing import Generator, List
from hashlib import md5
import src.config as config


def rand_bytes(num: int) -> bytes:
    if num < 1:
        raise ValueError("Cannot generate less than 1 byte!")
    return secrets.token_bytes(num)


def get_project_root() -> Path:
    return Path(__file__).parent.parent


# TODO: make more secure, now it will just generate 512 unique symbols before looping
def byte_cycling(b: bytes) -> Generator[int, None, None]:
    while True:
        for byte in b:
            yield byte


def hash_db() -> bytes:
    h = md5()
    with open(get_project_root() / config.db_name, "rb") as db_file:
        data = db_file.read(65536)
        while data:
            h.update(data)
            data = db_file.read(65536)
    return h.digest()
