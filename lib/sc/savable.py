import abc

from lib.utils import BinaryWriter


class Savable(abc.ABC):
    @abc.abstractmethod
    def save(self, stream: BinaryWriter):
        pass

    @abc.abstractmethod
    def get_tag(self) -> int:
        pass
