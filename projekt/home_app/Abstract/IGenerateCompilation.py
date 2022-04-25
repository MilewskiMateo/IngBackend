from abc import ABCMeta, abstractmethod
from typing import List
from pydantic.types import UUID1

class IGenerateCompilation(metaclass=ABCMeta):
    @abstractmethod
    def generateCompilation(timestamps: List[int]) -> UUID1:
        ...
