import src.utils as utils
from typing import List, Optional
import src.persistence as persistence
import src.config as config

class PasswordManager:
    def __init__(self, user_password: str):
        self.persistence_manager = persistence.Persistence(user_password)

    @property
    def seed(self) -> bytes:
        return self.persistence_manager.seed

    @property
    def services(self) -> List[persistence.Service]:
        return self.persistence_manager.get_services()

    def get_service(self, service: str) -> Optional[persistence.Service]:
        return self.persistence_manager.get_service(service)

    def add_service(self, name: str, length: int = config.default_length, iterations: int = config.default_iterations, alphabet: str = config.default_alphabet) -> bool:
        service = self.persistence_manager.get_service(name)
        if service is not None:
            return False
        service = persistence.Service(name, utils.rand_bytes(config.seed_length), length, iterations, alphabet)
        service.init_control_hash()
        self.persistence_manager.add_service(service)
        return True

    def generate(self, service_name: str) -> str:
        service = self.get_service(service_name)
        if not service:
            raise ValueError("Service does not  exist!")
        if not service.validate():
            raise ValueError("Something has changed and the password could not be recovered!")
        return service.generate()
