from lib.sc.savable import Savable
from lib.utils import BinaryWriter


class Matrix(Savable):
    def __init__(self,
                 a: int = 1,
                 b: int = 0,
                 c: int = 0,
                 d: int = 1,
                 tx: int = 0,
                 ty: int = 0) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.tx = tx
        self.ty = ty

    def load(self, swf, tag: int) -> None:
        divider = 1024 if tag == 8 else 65535

        self.a = swf.reader.read_int() / divider  # scale x
        self.b = swf.reader.read_int() / divider  # rotation x
        self.c = swf.reader.read_int() / divider  # rotation y
        self.d = swf.reader.read_int() / divider  # scale y

        self.tx = swf.reader.read_twip()  # position x
        self.ty = swf.reader.read_twip()  # position y

    def save(self, stream: BinaryWriter):
        stream.write_int(int(round(self.a * 1024)))
        stream.write_int(int(round(self.b * 1024)))
        stream.write_int(int(round(self.c * 1024)))
        stream.write_int(int(round(self.d * 1024)))

        stream.write_twip(self.tx)
        stream.write_twip(self.ty)

    def get_tag(self) -> int:
        return 8

    def __eq__(self, other):
        if isinstance(other, Matrix):
            if self.a == other.a and self.b == other.b and self.c == other.c and self.d == other.d and self.tx == other.tx and self.ty == other.ty:
                return True

        return False
