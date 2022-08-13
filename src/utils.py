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


class Generator:
    """Creates alphabet to which the cooked tokens will be translated. Ensures that there are present symbols from
    required groups."""

    def __init__(self, alphabet: str, length: int):
        self.alphabet = alphabet
        self.groups = None
        self._init_groups()
        self.charset = list(set(self.alphabet))
        self.charset.sort()
        self.length = length
        if len(self.groups) > self.length:
            raise ValueError("Cannot have more groups than symbols!")

    def _init_groups(self) -> None:
        """Translates the string-based alphabet syntax to an actual object. These strings are stored in the recipe."""
        marked_indices = []
        groups = []
        inside_brackets = False
        start_index = -1
        for index, letter in enumerate(self.alphabet):
            if letter == "\\" and index < len(self.alphabet) - 1:
                if self.alphabet[index + 1] == "[":
                    inside_brackets = True
                    start_index = index + 2
                elif (
                        self.alphabet[index + 1] == "]"
                        and inside_brackets
                        and (index - start_index) > 0
                ):
                    groups.append(self.alphabet[start_index:index])
                    inside_brackets = False
                    marked_indices.append(start_index - 2)
                    marked_indices.append(start_index - 1)
                    marked_indices.append(index)
                    marked_indices.append(index + 1)
                    start_index = -1
        self.groups = groups
        marked_indices.sort(reverse=True)
        for i in marked_indices:
            self.alphabet = self.alphabet[:i] + self.alphabet[i + 1:]

    def generate_password(self) -> str:
        """Maps bytes to a string output consisting of pre-selected symbols."""
        unused_indices = [i for i in range(self.length)]
        ans = {}
        data = rand_bytes(2 * self.length)
        iterator = byte_cycling(data)
        for group in self.groups:
            position = unused_indices[next(iterator) % len(unused_indices)]
            ans.update({position: group[next(iterator) % len(group)]})
            unused_indices.remove(position)
        for i in range(self.length - len(ans)):
            position = unused_indices[next(iterator) % len(unused_indices)]
            ans.update({position: self.charset[next(iterator) % len(self.charset)]})
            unused_indices.remove(position)
        password = ""
        for i in range(self.length):
            password += ans.get(i)
        return password
