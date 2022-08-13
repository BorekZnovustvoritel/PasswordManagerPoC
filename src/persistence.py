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
    """Decrypted service and password recipe."""

    def __init__(self, idx: int, name: str, encrypted_password: bytes, iv: bytes, persistence_manager: Persistence):
        self.persistence_manager = persistence_manager
        self.idx: int = idx
        self.name: str = name
        self.encrypted_password = encrypted_password
        self.iv = iv

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            f"<Service: idx='{self.idx}', name='{self.name}'>"
        )

    @property
    def password(self) -> str:
        """Generate the service's password."""
        cipher = AES.new(self.persistence_manager.token, AES.MODE_CBC, iv=self.iv)
        return unpad(cipher.decrypt(self.encrypted_password), 16).decode('utf-8')

    def change_name(self, name: str) -> bool:
        raise NotImplemented()
        pass

    def change_password(self, password: str) -> bool:
        raise NotImplemented()
        pass

class EncryptedService:
    """Encrypted service and its IVs."""

    def __init__(self, idx: int, e_name: bytes, e_password: bytes, iv_n: bytes, iv_p: bytes):
        self.idx = idx
        self.e_name = e_name
        self.e_password = e_password
        self.iv_n = iv_n
        self.iv_p = iv_p

    def decrypt(self, persistence_manager: Persistence) -> Service:
        """Creates Service from EncryptedService."""
        cipher = AES.new(persistence_manager.token, AES.MODE_CBC, iv=self.iv_n)
        name = unpad(cipher.decrypt(self.e_name), 16).decode('utf-8')
        return Service(self.idx, name, self.e_password, self.iv_p, persistence_manager)


class Persistence:
    """Communication with the database. Needs main password to decrypt the database."""

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
            "CREATE TABLE IF NOT EXISTS services"
            " (idx INTEGER PRIMARY KEY AUTOINCREMENT, e_name BLOB, e_password BLOB, iv_n BLOB, iv_p BLOB);"
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    @property
    def seed(self) -> Optional[bytes]:
        """Returns salt used for db encryption purposes. This salt is combined with the main password, hashed many
        times and the out-coming mess is used as the db encryption key."""
        seed = self.cursor.execute("SELECT seed FROM seeds;").fetchone()
        if not seed:
            return None
        else:
            seed = seed[0]
        return seed

    def get_services(self) -> List[Service]:
        """Get decrypted services and their recipes."""
        ans: List[Service] = []
        for row in self.cursor.execute("SELECT idx, e_name, e_password, iv_n, iv_p FROM services;"):
            e_service = EncryptedService(row[0], row[1], row[2], row[3], row[4])
            service = e_service.decrypt(self)
            ans.append(service)
        return ans

    def get_service(self, name: str) -> Optional[Service]:
        """Get decrypted service and its recipe"""
        services = self.get_services()
        return next((service for service in services if service.name == name), None)

    def add_service(self, name: str, password: str, ) -> bool:
        """Encrypt a service and add it to the database."""
        if not name or not password:
            return False
        cipher_n = AES.new(self.token, AES.MODE_CBC)
        iv_n = cipher_n.iv
        e_name = cipher_n.encrypt(pad(bytes(name, encoding='utf-8'), 16))
        cipher_p = AES.new(self.token, AES.MODE_CBC)
        iv_p = cipher_p.iv
        e_password = cipher_p.encrypt(pad(bytes(password, encoding='utf-8'), 16))
        try:
            self.cursor.execute(
                "INSERT INTO services (e_name, e_password, iv_n, iv_p) VALUES (?, ?, ?, ?);",
                (e_name, e_password, iv_n, iv_p),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def init_token(self, user_password: str) -> None:
        """Initiates the password decryption token. Combines main password with salt and hashes this mess many times."""
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
        """Initiates salt used for the database encryption."""
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

    def remove_service(self, service: Service) -> bool:
        """Removes a service."""
        if not service:
            return False
        self.cursor.execute("DELETE FROM services WHERE idx=?;", (service.idx,))
        self.conn.commit()
        return True
