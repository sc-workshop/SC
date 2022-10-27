from lib.sc.savable import Savable
from lib.utils import BinaryWriter


class Color(Savable):
    def __init__(self,
                 r_add: float = 0.0,
                 g_add: float = 0.0,
                 b_add: float = 0.0,
                 a_mul: float = 1.0,
                 r_mul: float = 1.0,
                 g_mul: float = 1.0,
                 b_mul: float = 1.0) -> None:
        self.r_add = r_add
        self.g_add = g_add
        self.b_add = b_add

        self.a_mul = a_mul
        self.r_mul = r_mul
        self.g_mul = g_mul
        self.b_mul = b_mul

    def load(self, swf, tag: int) -> None:
        self.r_add = swf.reader.read_uchar()
        self.g_add = swf.reader.read_uchar()
        self.b_add = swf.reader.read_uchar()

        self.a_mul = swf.reader.read_uchar() / 255
        self.r_mul = swf.reader.read_uchar() / 255
        self.g_mul = swf.reader.read_uchar() / 255
        self.b_mul = swf.reader.read_uchar() / 255

    def save(self, stream: BinaryWriter):
        stream.write_uchar(round(self.r_add))
        stream.write_uchar(round(self.g_add))
        stream.write_uchar(round(self.b_add))

        stream.write_uchar(round(self.a_mul * 255))
        stream.write_uchar(round(self.r_mul * 255))
        stream.write_uchar(round(self.g_mul * 255))
        stream.write_uchar(round(self.b_mul * 255))

    def get_tag(self) -> int:
        return 9
