import secrets
from pathlib import Path
from typing import Generator, List
from hashlib import md5
import src.config as config


def rand_bytes(num: int) -> bytes:
    """Generates `num` of pseudorandom bytes."""
    if num < 1:
        raise ValueError("Cannot generate less than 1 byte!")
    return secrets.token_bytes(num)


def get_project_root() -> Path:
    """Returns project's root directory."""
    return Path(__file__).parent.parent


# TODO: make more secure, now it will just generate 512 unique symbols before looping
def byte_cycling(b: bytes) -> Generator[int, None, None]:
    """Creates a generator that will cycle infinitely through input bytes."""
    while True:
        for byte in b:
            yield byte


def hash_db() -> bytes:
    """Returns hash of the .db file."""
    h = md5()
    with open(get_project_root() / config.db_name, "rb") as db_file:
        data = db_file.read(65536)
        while data:
            h.update(data)
            data = db_file.read(65536)
    return h.digest()


def is_first_init() -> bool:
    """Determines if the user has already created a profile."""
    return not (get_project_root() / config.db_name).is_file()
