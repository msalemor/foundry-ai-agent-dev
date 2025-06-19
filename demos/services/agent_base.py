from abc import ABC, abstractmethod


class AgentBase(ABC):
    @abstractmethod
    def process(self, query: str) -> str:
        pass
