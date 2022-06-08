import src.utils as utils
from typing import List, Optional
import src.persistence as persistence
import src.config as config


class PasswordManager:
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

    def get_service(self, service: str) -> Optional[persistence.Service]:
        return self.persistence_manager.get_service(service)

    def add_service(
        self,
        name: str,
        length: int = config.default_length,
        iterations: int = config.default_iterations,
        alphabet: str = config.default_alphabet,
    ) -> bool:
        if not isinstance(length, int) or length < 8:
            raise ValueError("Weak password length!")
        if not isinstance(iterations, int) or iterations < 1:
            raise ValueError("Cannot perform less than 1 iteration!")
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
        service = persistence.Service(
            name, utils.rand_bytes(config.seed_length), length, iterations, alphabet
        )
        service.init_control_hash()
        self.persistence_manager.add_service(service)
        return True

    def generate(self, service_name: str) -> str:
        service = self.get_service(service_name)
        if not service:
            raise ValueError("Service does not  exist!")
        if not service.validate():
            raise ValueError(
                "Something has changed and the password could not be recovered!"
            )
        return service.generate()

    def remove_service(self, name: str) -> str:
        if not isinstance(name, str):
            raise TypeError("Service name must be a string!")
        if not self.persistence_manager.remove_service(name):
            return "Not found."
        return f"Successfully deleted service {name}."
