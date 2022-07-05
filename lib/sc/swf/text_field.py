from .writable import Writable


class TextField(Writable):
    def __init__(self) -> None:
        self.id: int = -1

        self.font_name: str = None
        self.font_color: int = -1
        self.outline_color: int = None # -1
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

        self.flag1: bool = None # False
        self.flag2: bool = None # False
        self.flag3: bool = None # False

        self.c1: int = None # 0
        self.c2: int = None # 0
    
    def load(self, swf, tag: int):
        self.id = swf.reader.read_ushort()

        swf.text_fields_ids.append(self.id)

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
    
    def save(self):
        super().save()

        tag = 7

        self.write_ushort(self.id)

        self.write_ascii(self.font_name)
        self.write_int(self.font_color)

        self.write_bool(self.bold)
        self.write_bool(self.italic)
        self.write_bool(self.multiline)
        self.write_bool(False) # unused

        self.write_uchar(self.font_align)
        self.write_uchar(self.font_size)

        self.write_short(self.left_corner)
        self.write_short(self.top_corner)
        self.write_short(self.right_corner)
        self.write_short(self.bottom_corner)

        self.write_bool(self.uppercase)
        self.write_ascii(self.text)

        # TODO: change this shit code
        if self.flag1 is not None:
            tag = 15
            self.write_bool(self.flag1)

            if self.flag2 is not None:
                if self.flag2:
                    tag = 20
                else:
                    if self.outline_color is not None:
                        tag = 21
                        self.write_int(self.outline_color)

                        if self.c1 is not None:
                            tag = 25
                            self.write_short(self.c1)
                            self.write_short(0) # unused

                            if self.c2 is not None:
                                tag = 33
                                self.write_short(self.c2)

                                if self.flag3 is not None:
                                    tag = 43
                                    if self.flag3:
                                        tag = 44
                                        self.write_bool(self.flag3)

        return tag, self.buffer
