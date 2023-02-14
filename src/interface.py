from __future__ import annotations

from enum import Enum

from typing import List, Optional
import src.persistence as persistence
from src import config as config
from src.utils import rand_bytes, byte_cycling


class Generator:
    """Creates alphabet to which the cooked tokens will be translated. Ensures that there are present symbols from
    required groups."""

    def __init__(self, alphabet: Alphabet, length: int):
        self.alphabet = alphabet
        self.length = length

    def generate_password(self) -> str:
        """Maps bytes to a string output consisting of pre-selected symbols."""
        unused_indices = [i for i in range(self.length)]
        ans = {}
        data = rand_bytes(2 * self.length)
        iterator = byte_cycling(data)
        for group in self.alphabet.groups:
            position = unused_indices[next(iterator) % len(unused_indices)]
            ans.update({position: group[next(iterator) % len(group)]})
            unused_indices.remove(position)
        for i in range(self.length - len(ans)):
            position = unused_indices[next(iterator) % len(unused_indices)]
            ans.update({position: self.alphabet.symbol_pool[next(iterator) % len(self.alphabet.symbol_pool)]})
            unused_indices.remove(position)
        password = ""
        for i in range(self.length):
            password += ans.get(i)
        return password


class Usage(Enum):
    DISALLOW = 0
    ALLOW = 1
    ENFORCE = 2


class Alphabet:
    def __init__(self, lowercase: Usage, uppercase: Usage, numbers: Usage, specials: Usage,
                 specials_to_use: str = config.default_special_characters):
        self.groups: List[str] = []
        self.symbol_pool: str = ''
        if lowercase == Usage.ENFORCE:
            self.groups.append(config.lowercase)
            self.symbol_pool += config.lowercase
        elif lowercase == Usage.ALLOW:
            self.symbol_pool += config.lowercase
        if uppercase == Usage.ENFORCE:
            self.groups.append(config.uppercase)
            self.symbol_pool += config.uppercase
        elif uppercase == Usage.ALLOW:
            self.symbol_pool += config.uppercase
        if numbers == Usage.ENFORCE:
            self.groups.append(config.numbers)
            self.symbol_pool += config.numbers
        elif numbers == Usage.ALLOW:
            self.symbol_pool += config.numbers
        if specials == Usage.ENFORCE:
            self.groups.append(specials_to_use)
            self.symbol_pool += specials_to_use
        elif specials == Usage.ALLOW:
            self.symbol_pool += specials_to_use
        if len(self.symbol_pool) < 10:
            raise ValueError("This alphabet set would be too weak!")


class PasswordManager:
    """String-based interface for the application."""

    def __init__(self, user_password: str):
        if not isinstance(user_password, str):
            raise TypeError("Application password must be a string!")
        self.persistence_manager = persistence.Persistence(user_password)

    @property
    def seed(self) -> bytes:
        return self.persistence_manager.seed

    @property
    def services(self) -> List[persistence.Service]:
        return self.persistence_manager.get_services()

    def get_service(self, idx: int) -> Optional[persistence.Service]:
        return self.persistence_manager.get_service(idx)

    def add_service(
            self,
            name: str,
            length: int = config.default_length,
            alphabet: Alphabet = Alphabet(Usage.ENFORCE, Usage.ENFORCE, Usage.ENFORCE,
                                          Usage.ENFORCE),
            password: str = None
    ) -> bool:
        """Add a service."""
        if password:
            self.persistence_manager.add_service(name, password)
            return True
        if not isinstance(length, int):
            raise ValueError("Length must be instance of int!")
        if config.seed_length < 1:
            raise ValueError(
                "There has to be at least some cryptographic salt!"
                " src.config.seed_length must be grater than 0!"
            )
        self.persistence_manager.add_service(name, Generator(alphabet, length).generate_password())
        return True

    def remove_service(self, idx: int) -> str:
        """Remove the service according to its name."""
        if not isinstance(idx, int):
            raise TypeError("Service idx must be an integer!")
        service = self.get_service(idx)
        if not self.persistence_manager.remove_service(service):
            return "Not found."
        return f"Successfully deleted service {service.name}."

