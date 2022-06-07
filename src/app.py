import src.utils as utils
from typing import List, Optional
import src.persistence as persistence
import src.config as config
from hashlib import sha3_512

class PasswordManager:
    def __init__(self):
        pass

    @property
    def seed(self) -> bytes:
        persistence_manager = persistence.Persistence()
        seed = persistence_manager.seed
        persistence_manager.close()
        return seed

    @property
    def services(self) -> List[persistence.Service]:
        persistence_manager = persistence.Persistence()
        services = persistence_manager.get_services()
        persistence_manager.close()
        return services

    def get_service(self, service: str) -> Optional[persistence.Service]:
        persistence_manager = persistence.Persistence()
        service = persistence_manager.get_service(service)
        persistence_manager.close()
        return service

    def add_service(self, name: str, length: int = config.default_length, iterations: int = config.default_iterations, alphabet: str = config.default_alphabet) -> bool:
        persistence_manager = persistence.Persistence()
        service = persistence_manager.get_service(name)
        if service is not None:
            persistence_manager.close()
            return False
        service = persistence.Service(name, utils.rand_bytes(config.seed_length), length, iterations, alphabet)
        service._init_control_hash()
        persistence_manager.add_service(service)
        persistence_manager.close()
        return True

    def generate(self, service_name: str) -> str:
        service = self.get_service(service_name)
        if not service:
            raise ValueError("Service does not  exist!")
        if not service.validate():
            raise ValueError("Something has changed and the password could not be recovered!")
        return service.generate()
