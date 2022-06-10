from __future__ import annotations
import sqlite3
from typing import List, Optional
from src.utils import get_project_root, rand_bytes, byte_cycling
from src.config import seed_length, db_name, auth_iterations
from hashlib import sha3_512, sha3_256
import pickle

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class Service:
    def __init__(
        self, name: str, seed: bytes, length: int, iterations: int, alphabet: str
    ):
        self.name: str = name
        self.seed: bytes = seed
        self.length: int = length
        self.iterations: int = iterations
        self.alphabet: str = alphabet
        self.control_hash: bytes = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            f"<Service: name='{self.name}', seed={self.seed}, length={self.length}, "
            f"iterations={self.iterations}, alphabet='{self.alphabet}'>"
        )

    def generate(self) -> str:
        if self.iterations < 1:
            raise ValueError("Cannot iterate less times than 1!")
        h = sha3_512()
        h.update(bytes(self.name, encoding="utf-8") + self.seed)
        digest = None
        for i in range(self.iterations):
            digest = h.digest()
            h.update(digest)
        service_map = MapAlphabet(self)
        return service_map.generate_password(digest)

    def _control_hash(self) -> bytes:
        h = sha3_512()
        h.update(bytes(self.generate(), encoding="utf-8"))
        return h.digest()

    def init_control_hash(self) -> None:
        if self.control_hash is not None:
            raise ValueError("Rewriting control hash is forbidden!")
        self.control_hash = self._control_hash()

    def validate(self) -> bool:
        if self._control_hash() != self.control_hash:
            return False
        return True

    def encrypt(self, persistence_manager: Persistence) -> EncryptedService:
        blob = pickle.dumps(self)
        cipher = AES.new(persistence_manager.token, AES.MODE_CBC)
        iv = cipher.iv
        cipher_blob = cipher.encrypt(pad(blob, 16))
        return EncryptedService(cipher_blob, iv)


class EncryptedService:
    def __init__(self, blob, iv):
        self.blob = blob
        self.iv = iv

    def decrypt(self, persistence_manager: Persistence) -> Service:
        cipher = AES.new(persistence_manager.token, AES.MODE_CBC, iv=self.iv)
        return pickle.loads(unpad(cipher.decrypt(self.blob), 16))


class Persistence:
    def __init__(self, user_password: str):
        if not db_name:
            self.conn = sqlite3.connect(get_project_root() / "pswdmngr.db")
        else:
            self.conn = sqlite3.connect(get_project_root() / db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS seeds (seed BLOB, iterations INT, controlhash BLOB);"
        )
        if not self.seed:
            self.set_password(user_password)
        self.token: bytes = None
        self.init_token(user_password)

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS services (idx INTEGER PRIMARY KEY AUTOINCREMENT, e_data BLOB, iv BLOB);"
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    @property
    def seed(self) -> Optional[bytes]:
        seed = self.cursor.execute("SELECT seed FROM seeds;").fetchone()
        if not seed:
            return None
        else:
            seed = seed[0]
        return seed

    def get_services(self) -> List[Service]:
        ans: List = []
        for row in self.cursor.execute("SELECT e_data, iv FROM services;"):
            e_service = EncryptedService(row[0], row[1])
            service = e_service.decrypt(self)
            ans.append(service)
        return ans

    def get_service(self, name: str) -> Optional[Service]:
        services = self.get_services()
        return next((service for service in services if service.name == name), None)

    def add_service(self, service: Service) -> None:
        e_service = service.encrypt(self)
        self.cursor.execute(
            "INSERT INTO services (e_data, iv) VALUES (?, ?);", (e_service.blob, e_service.iv)
        )
        self.conn.commit()

    def init_token(self, user_password: str) -> None:
        h = sha3_256()
        h.update(self.seed + bytes(user_password, encoding="utf-8"))
        digest = None
        iterations = self.cursor.execute("SELECT iterations FROM seeds;").fetchone()[0]
        for i in range(iterations):
            digest = h.digest()
            h.update(digest)
        h2 = sha3_512()
        h2.update(digest)
        control_hash = self.cursor.execute("SELECT controlhash FROM seeds;").fetchone()[
            0
        ]
        if control_hash != h2.digest():
            raise ValueError("Incorrect password!")
        self.token = digest

    def set_password(self, user_password: str) -> None:
        if seed_length < 1:
            raise ValueError(
                "There has to be at least some cryptographic salt!"
                " src.config.seed_length must be grater than 0!"
            )
        if auth_iterations < 1:
            raise ValueError("Cannot perform less than 1 iteration!")
        h = sha3_256()
        seed = rand_bytes(seed_length)
        h.update(seed + bytes(user_password, encoding="utf-8"))
        digest = None
        for i in range(auth_iterations):
            digest = h.digest()
            h.update(digest)
        h2 = sha3_512()
        h2.update(digest)
        self.cursor.execute(
            "INSERT INTO seeds VALUES (?, ?, ?);", (seed, auth_iterations, h2.digest())
        )
        self.conn.commit()

    def remove_service(self, name: str) -> bool:
        service = self.get_service(name)
        if not service:
            return False
        for row in self.cursor.execute("SELECT idx, e_data, iv FROM services;"):
            e_service = EncryptedService(row[1], row[2])
            service = e_service.decrypt(self)
            idx = row[0]
            if service.name == name:
                self.cursor.execute("DELETE FROM services WHERE idx=?;", (idx,))
        self.conn.commit()
        return True


class MapAlphabet:
    def __init__(self, service: Service):
        self.raw_service = service
        self.alphabet = service.alphabet
        self.groups = None
        self.init_groups()
        self.charset = list(set(self.alphabet))
        self.charset.sort()
        if len(self.groups) > self.raw_service.length:
            raise ValueError("Cannot have more groups than symbols!")

    def init_groups(self) -> None:
        marked_indices = []
        groups = []
        inside_brackets = False
        start_index = -1
        for index, letter in enumerate(self.alphabet):
            if letter == "\\" and index < len(self.alphabet) - 1:
                if self.alphabet[index + 1] == "[":
                    inside_brackets = True
                    start_index = index + 2
                elif self.alphabet[index + 1] == "]" and inside_brackets and (index - start_index) > 0:
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

    def generate_password(self, data: bytes) -> str:
        unused_indices = [i for i in range(self.raw_service.length)]
        ans = {}
        iterator = byte_cycling(data)
        for group in self.groups:
            position = unused_indices[next(iterator) % len(unused_indices)]
            ans.update({position: group[next(iterator) % len(group)]})
            unused_indices.remove(position)
        for i in range(self.raw_service.length - len(ans)):
            position = unused_indices[next(iterator) % len(unused_indices)]
            ans.update({position: self.charset[next(iterator) % len(self.charset)]})
            unused_indices.remove(position)
        password = ""
        for i in range(self.raw_service.length):
            password += ans.get(i)
        return password
