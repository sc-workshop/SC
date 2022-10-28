from lib.sc.savable import Savable
from lib.utils import BinaryWriter


class MovieClipFrame(Savable):
    def __init__(self) -> None:
        self.elements: list = []
        self.name: str or None = None

    def load(self, swf):
        elements_count = swf.reader.read_ushort()
        self.name = swf.reader.read_ascii()

        return elements_count

    def save(self, stream: BinaryWriter):
        stream.write_ushort(len(self.elements))
        stream.write_ascii(self.name)

    def get_tag(self) -> int:
        return 11

    def __eq__(self, other):
        if isinstance(other, MovieClipFrame):
            if self.name == other.name and self.elements == other.elements:
                return True
        return False
