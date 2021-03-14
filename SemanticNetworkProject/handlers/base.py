from abc import ABC, abstractmethod
from typing import Iterable, Set, NamedTuple
from extractor.relations.base import Relation

class AbstractRelationsHandler(ABC):
    """Handles relations."""
    @abstractmethod
    def handle(self, relations: Iterable[Relation]):
        pass