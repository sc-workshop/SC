from lib.sc.movie_clip.modifier import Modifier
from lib.sc.resource import Resource
from lib.sc.savable import Savable
from lib.utils import BinaryWriter


class MovieClipModifier(Resource, Savable):
    def __init__(self) -> None:
        super().__init__()

        self.modifier: Modifier = Modifier.Mask

    def load(self, swf, tag: int) -> None:
        self.modifier = Modifier(tag)
        self.id = swf.reader.read_ushort()

    def save(self, stream: BinaryWriter):
        stream.write_ushort(self.id)

    def get_tag(self) -> int:
        # noinspection PyTypeChecker
        return self.modifier.value

    def __eq__(self, other):
        if isinstance(other, MovieClipModifier):
            if self.modifier == other.modifier:
                return True

        return False


def save_movie_clip_modifiers_count(count: int):
    def wrapper(stream: BinaryWriter):
        stream.write_ushort(count)
    return wrapper
