import src.utils as utils
from typing import List, Optional
import src.persistence as persistence
import src.config as config


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

    def get_service(self, name: str) -> Optional[persistence.Service]:
        return self.persistence_manager.get_service(name)

    def add_service(
            self,
            name: str,
            length: int = config.default_length,
            alphabet: str = config.default_alphabet,
    ) -> bool:
        """Add a service."""
        if not isinstance(length, int) or length < 8:
            raise ValueError("Weak password length!")
        if not isinstance(alphabet, str) or len(set(alphabet)) < 10:
            raise ValueError("Weak alphabet set!")
        if config.seed_length < 1:
            raise ValueError(
                "There has to be at least some cryptographic salt!"
                " src.config.seed_length must be grater than 0!"
            )
        service = self.persistence_manager.get_service(name)
        if service is not None:
            return False
        self.persistence_manager.add_service(name, utils.Generator(alphabet, length).generate_password())
        return True



    def remove_service(self, name: str) -> str:
        """Remove the service according to its name."""
        if not isinstance(name, str):
            raise TypeError("Service name must be a string!")
        if not self.persistence_manager.remove_service(self.get_service(name)):
            return "Not found."
        return f"Successfully deleted service {name}."
