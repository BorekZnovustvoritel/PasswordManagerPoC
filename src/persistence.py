from __future__ import annotations
import sqlite3
from typing import List, Optional
from src.utils import get_project_root, rand_bytes, byte_cycling
from src.config import seed_length, db_name
from hashlib import sha3_512


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

    def _init_control_hash(self):
        self.control_hash = self._control_hash()

    def validate(self) -> bool:
        if self._control_hash() != self.control_hash:
            return False
        return True


class Persistence:
    def __init__(self):
        self.conn = sqlite3.connect(get_project_root() / db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS services (service TEXT, seed BLOB, length INT, iterations INT, alphabet TEXT, controlhash BLOB NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS seeds (seed BLOB);")
        self.conn.commit()

    @property
    def seed(self) -> bytes:
        seed = self.cursor.execute("SELECT seed FROM seeds;").fetchone()
        if not seed:
            seed = rand_bytes(seed_length)
            self.cursor.execute("INSERT INTO seeds VALUES (?)", (seed,))
            self.conn.commit()
        else:
            seed = seed[0]
        return seed

    def get_services(self) -> List[Service]:
        ans: List = []
        for row in self.cursor.execute("SELECT service, seed, length, iterations, alphabet, controlhash FROM services"):
            service = Service(str(row[0]), bytes(row[1]), int(row[2]), int(row[3]), str(row[4]))
            service.control_hash = bytes(row[5])
            ans.append(service)
        return ans

    def get_service(self, name: str) -> Optional[Service]:
        result = self.cursor.execute("SELECT service, seed, length, iterations, alphabet, controlhash FROM services WHERE service=?", (name,)).fetchone()
        if not result:
            return None
        service = Service(str(result[0]), bytes(result[1]), int(result[2]), int(result[3]), str(result[4]))
        service.control_hash = result[5]
        return service

    def add_service(self, service: Service) -> None:
        self.cursor.execute("INSERT INTO services VALUES (?, ?, ?, ?, ?, ?)", (service.name, service.seed, service.length, service.iterations, service.alphabet, service.control_hash))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
