from abc import ABCMeta, abstractmethod
from typing import List
from pydantic.types import UUID1

class IStreamCompilation(metaclass=ABCMeta):
    @abstractmethod
    def IStreamCompilation(id: str, start: int, end: int) -> dict:
        ...
