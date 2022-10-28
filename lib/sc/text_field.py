from .resource import Resource
from .savable import Savable
from ..utils import BinaryWriter


class TextField(Resource, Savable):
    def __init__(self) -> None:
        super().__init__()

        self.font_name: str or None = None
        self.font_color: int = -1
        self.outline_color: int or None = None  # -1
        self.font_size: int = 0
        self.font_align: int = 0

        self.bold: bool = False
        self.italic: bool = False
        self.multiline: bool = False
        self.outline: bool = False

        self.left_corner: int = 0
        self.top_corner: int = 0
        self.right_corner: int = 0
        self.bottom_corner: int = 0

        self.text: str or None = None

        self.flag1: bool or None = None  # False
        self.flag2: bool or None = None  # False
        self.flag3: bool or None = None  # False

        self.c1: int or None = None  # 0
        self.c2: int or None = None  # 0

    def load(self, swf, tag: int) -> None:
        self.id = swf.reader.read_ushort()

        self.font_name = swf.reader.read_ascii()
        self.font_color = swf.reader.read_int()

        self.bold = swf.reader.read_bool()
        self.italic = swf.reader.read_bool()
        self.multiline = swf.reader.read_bool()
        swf.reader.read_bool()  # unused

        self.font_align = swf.reader.read_uchar()
        self.font_size = swf.reader.read_uchar()

        self.top_corner = swf.reader.read_short()
        self.bottom_corner = swf.reader.read_short()
        self.left_corner = swf.reader.read_short()
        self.right_corner = swf.reader.read_short()

        self.outline = swf.reader.read_bool()
        self.text = swf.reader.read_ascii()

        if tag == 7:
            return self.id

        self.flag1 = swf.reader.read_bool()

        if tag > 15:
            self.flag2 = tag != 25

        if tag > 20:
            self.outline_color = swf.reader.read_int()

        if tag > 25:
            self.c1 = swf.reader.read_short()
            swf.reader.read_short()  # unused

        if tag > 33:
            self.c2 = swf.reader.read_short()

        if tag > 43:
            self.flag3 = swf.reader.read_bool()

    def save(self, stream: BinaryWriter):
        stream.write_ushort(self.id)

        stream.write_ascii(self.font_name)
        stream.write_int(self.font_color)

        stream.write_bool(self.bold)
        stream.write_bool(self.italic)
        stream.write_bool(self.multiline)
        stream.write_bool(False)  # unused

        stream.write_uchar(self.font_align)
        stream.write_uchar(self.font_size)

        stream.write_short(self.top_corner)
        stream.write_short(self.bottom_corner)
        stream.write_short(self.left_corner)
        stream.write_short(self.right_corner)

        stream.write_bool(self.outline)
        stream.write_ascii(self.text)

        if self.flag1 is not None:
            stream.write_bool(self.flag1)

            if self.flag2 is not None:
                if not self.flag2:
                    if self.outline_color is not None:
                        stream.write_int(self.outline_color)

                        if self.c1 is not None:
                            stream.write_short(self.c1)
                            stream.write_short(0)  # unused

                            if self.c2 is not None:
                                stream.write_short(self.c2)

                                if self.flag3 is not None:
                                    if self.flag3:
                                        stream.write_bool(self.flag3)

    def get_tag(self) -> int:
        if self.flag1 is None:
            return 7
        if self.flag2 is None or self.outline_color is None:
            return 15
        if self.flag2:
            return 20

        if self.c1 is None:
            return 21
        if self.c2 is None:
            return 25

        if self.flag3 is None:
            return 33

        if self.flag3:
            return 44
        else:
            return 43

    def __eq__(self, other):
        if isinstance(other, TextField):
            if self.font_name == other.font_name \
                    and self.font_color == other.font_color \
                    and self.outline_color == other.outline_color \
                    and self.font_size == other.font_size \
                    and self.font_size == other.font_size \
                    and self.font_align == other.font_align \
                    and self.bold == other.bold \
                    and self.italic == other.italic \
                    and self.multiline == other.multiline \
                    and self.left_corner == other.left_corner \
                    and self.top_corner == other.top_corner \
                    and self.right_corner == other.right_corner \
                    and self.bottom_corner == other.bottom_corner \
                    and self.text == other.text \
                    and self.flag1 == other.flag1 \
                    and self.flag2 == other.flag2 \
                    and self.flag3 == other.flag3 \
                    and self.c1 == other.c1 \
                    and self.c2 == other.c2:
                return True
        return False
