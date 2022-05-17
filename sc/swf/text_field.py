from sc.utils import BinaryWriter


class TextField:
    def __init__(self) -> None:
        self.id: int = -1

        self.font_name: str = None
        self.font_color: int = -1
        self.outline_color: int = -1
        self.font_size: int = 0
        self.font_align: int = 0

        self.bold: bool = False
        self.italic: bool = False
        self.multiline: bool = False
        self.uppercase: bool = False

        self.left_corner: int = 0
        self.top_corner: int = 0
        self.right_corner: int = 0
        self.bottom_corner: int = 0

        self.text: str = None

        self.flag1: bool = False
        self.flag2: bool = False
        self.flag3: bool = False

        self.c1: int = 0
        self.c2: int = 0
    
    def load(self, swf, tag: int):
        self.id = swf.reader.read_ushort()

        self.font_name = swf.reader.read_ascii()
        self.font_color = swf.reader.read_int()

        self.bold = swf.reader.read_bool()
        self.italic = swf.reader.read_bool()
        self.multiline = swf.reader.read_bool()
        swf.reader.read_bool() # unused

        self.font_align = swf.reader.read_uchar()
        self.font_size = swf.reader.read_uchar()

        self.left_corner = swf.reader.read_short()
        self.top_corner = swf.reader.read_short()
        self.right_corner = swf.reader.read_short()
        self.bottom_corner = swf.reader.read_short()

        self.uppercase = swf.reader.read_bool()
        self.text = swf.reader.read_ascii()

        if tag == 7: return

        self.flag1 = swf.reader.read_bool()

        if tag > 15:
            self.flag2 = tag != 25

        if tag > 20:
            self.outline_color = swf.reader.read_int()
        
        if tag > 25:
            self.c1 = swf.reader.read_short()
            swf.reader.read_short() # unused
        
        if tag > 33:
            self.c2 = swf.reader.read_short()
        
        if tag > 43:
            self.flag3 = swf.reader.read_bool()
    
    def save(self, swf):
        stream = BinaryWriter()

        tag = 7

        stream.write_ushort(self.id)

        stream.write_ascii(self.font_name)
        stream.write_int(self.font_color)

        stream.write_bool(self.bold)
        stream.write_bool(self.italic)
        stream.write_bool(self.multiline)
        stream.write_bool(False) # unused

        stream.write_uchar(self.font_align)
        stream.write_uchar(self.font_size)

        stream.write_short(self.left_corner)
        stream.write_short(self.top_corner)
        stream.write_short(self.right_corner)
        stream.write_short(self.bottom_corner)

        stream.write_bool(self.uppercase)
        stream.write_ascii(self.text)

        return tag, stream.buffer
