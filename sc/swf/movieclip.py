from sc.utils import BinaryWriter


BLENDMODES = [
    "Mix",
    "Mix",
    "Layer",
    "Multipliy",
    "Screen",
    "Lighten",
    "Darken",
    "Difference",
    "Add"
]


class MovieClipModifier:
    def __init__(self) -> None:
        self.id: int = -1
        self.stencil: int = 2
    
    def load(self, swf, tag: int):
        self.id = swf.reader.read_ushort()

        self.stencil = 2
        if tag == 39:
            self.stencil = 3
        elif tag == 40:
            self.stencil = 4
    
    def save(self):
        stream = BinaryWriter()

        stream.write_ushort(self.id)

        tag = 38
        if self.stencil == 3:
            tag = 39
        elif self.stencil == 4:
            tag = 40
        
        return tag, stream.buffer


class MovieClip:
    def __init__(self) -> None:
        self.id: int = -1

        self.frame_rate: int = 30
        self.binds: list = []
        self.frames: list = []

        self.nine_slice: list = []
        self.matrix_bank: int = 0
    
    def load(self, swf, tag: int):
        self.id = swf.reader.read_ushort()

        self.frame_rate = swf.reader.read_uchar()
        frames_count = swf.reader.read_ushort()
        self.frames = [_class() for _class in [MovieClipFrame] * frames_count]

        if tag in [3, 14]:
            return
        
        frame_elements = []
        frame_elements_count = swf.reader.read_int()
        for x in range(frame_elements_count):
            bind_index = swf.reader.read_ushort()
            matrix_index = swf.reader.read_ushort()
            color_index = swf.reader.read_ushort()

            frame_elements.append({
                "bind": bind_index,
                "matrix": matrix_index,
                "color": color_index
            })
        
        binds_count = swf.reader.read_ushort()

        for x in range(binds_count):
            self.binds.append({
                "id": swf.reader.read_ushort(),
                "blend": BLENDMODES[0]
            })
        
        if tag in [12, 35]:
            for x in range(binds_count):
                self.binds[x]["blend"] = BLENDMODES[swf.reader.read_uchar() & 0x3F]
        
        for x in range(binds_count):
            self.binds[x]["name"] = swf.reader.read_ascii()
        
        frames_loaded = 0
        frame_elements_offset = 0
        while True:
            frame_tag = swf.reader.read_uchar()
            frame_tag_length = swf.reader.read_int()

            if frame_tag == 0:
                break

            if frame_tag == 11:
                elements_count = self.frames[frames_loaded].load(swf)
                
                for x in range(elements_count):
                    self.frames[frames_loaded].elements.append(frame_elements[frame_elements_offset + x])
                frame_elements_offset += elements_count

                frames_loaded += 1
                continue

            elif frame_tag == 31:
                self.nine_slice = [0, 0, 0, 0]

                self.nine_slice[0] = swf.reader.read_twip()
                self.nine_slice[1] = swf.reader.read_twip()
                self.nine_slice[2] = swf.reader.read_twip()
                self.nine_slice[3] = swf.reader.read_twip()

                continue

            elif frame_tag == 41:
                self.matrix_bank = swf.reader.read_uchar()
                continue

            swf.reader.skip(frame_tag_length)
    
    def save(self, swf):
        stream = BinaryWriter()

        stream.write_ushort(self.id)
        stream.write_uchar(self.frame_rate)
        stream.write_ushort(len(self.frames))

        return 12, stream.buffer


class MovieClipFrame:
    def __init__(self) -> None:
        self.elements: list = []
        self.name: str = None
    
    def load(self, swf):
        elements_count = swf.reader.read_ushort()
        self.name = swf.reader.read_ascii()

        return elements_count
