from __future__ import annotations
import sqlite3
from typing import List, Optional
from src.utils import get_project_root, rand_bytes, byte_cycling
from src.config import seed_length, db_name, auth_iterations
from hashlib import sha3_512, sha3_256

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class Service:
    def __init__(self, name: str, seed: bytes, length: int, iterations: int, alphabet: str):
        self.name: str = name
        self.seed: bytes = seed
        self.length: int = length
        self.iterations: int = iterations
        self.alphabet: str = alphabet
        self.control_hash: bytes = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<Service: name={self.name}, seed={self.seed}, length={self.length}, iterations={self.iterations}, alphabet={self.alphabet}>"

    def generate(self) -> str:
        if self.iterations < 1:
            raise ValueError("Cannot iterate less times than 1!")
        h = sha3_512()
        h.update(bytes(self.name, encoding="utf-8") + self.seed)
        digest = None
        for i in range(self.iterations):
            digest = h.digest()
            h.update(digest)
        index = 0
        word: str = ""
        for b in byte_cycling(digest):
            if index >= self.length:
                break
            word += self.alphabet[b % len(self.alphabet)]
            index += 1
        return word

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
        blob = bytes(self.name, encoding="utf-8") + b'==' + self.seed + b'==' + \
               self.length.to_bytes(64, byteorder="big") + b'==' + self.iterations.to_bytes(64,
                                                                                            byteorder="big") + b'==' + \
               bytes(self.alphabet, encoding="utf-8") + b'==' + self.control_hash
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
        plain_blob = unpad(cipher.decrypt(self.blob), 16)
        blob_list = plain_blob.split(b'==')
        service = Service(blob_list[0].decode("utf-8"), blob_list[1], int.from_bytes(blob_list[2], "big"),
                          int.from_bytes(blob_list[3], "big"), blob_list[4].decode("utf-8"))
        service.control_hash = blob_list[5]
        return service


class Persistence:
    def __init__(self, user_password: str):
        self.conn = sqlite3.connect(get_project_root() / db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS seeds (seed BLOB, iterations INT, controlhash BLOB);")
        if not self.seed:
            self.set_password(user_password)
        self.token: bytes = None
        self.init_token(user_password)

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS services (e_data BLOB, iv BLOB);")
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
        for row in self.cursor.execute("SELECT e_data, iv FROM services"):
            e_service = EncryptedService(row[0], row[1])
            service = e_service.decrypt(self)
            ans.append(service)
        return ans

    def get_service(self, name: str) -> Optional[Service]:
        services = self.get_services()
        return next((service for service in services if service.name == name), None)

    def add_service(self, service: Service) -> None:
        e_service = service.encrypt(self)
        self.cursor.execute("INSERT INTO services VALUES (?, ?)", (e_service.blob, e_service.iv))
        self.conn.commit()

    def init_token(self, user_password: str) -> None:
        h = sha3_256()
        h.update(self.seed + bytes(user_password, encoding="utf-8"))
        digest = None
        iterations = self.cursor.execute("SELECT iterations FROM seeds").fetchone()[0]
        for i in range(iterations):
            digest = h.digest()
            h.update(digest)
        h2 = sha3_512()
        h2.update(digest)
        control_hash = self.cursor.execute("SELECT controlhash FROM seeds;").fetchone()[0]
        if control_hash != h2.digest():
            raise ValueError("Incorrect password!")
        self.token = digest

    def set_password(self, user_password: str) -> None:
        h = sha3_256()
        seed = rand_bytes(seed_length)
        h.update(seed + bytes(user_password, encoding="utf-8"))
        digest = None
        for i in range(auth_iterations):
            digest = h.digest()
            h.update(digest)
        h2 = sha3_512()
        h2.update(digest)
        self.cursor.execute("INSERT INTO seeds VALUES (?, ?, ?)", (seed, auth_iterations, h2.digest()))
        self.conn.commit()
