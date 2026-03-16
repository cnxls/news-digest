from abc import ABC, abstractmethod


class BaseDelivery(ABC):
    @abstractmethod
    def deliver(self, digest: str) -> bool:
        pass
