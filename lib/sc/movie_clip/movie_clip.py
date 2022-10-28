from typing import List, Tuple

from lib.console import Console
from lib.sc.movie_clip.movie_clip_frame import MovieClipFrame
from lib.sc.resource import Resource
from lib.sc.savable import Savable
from lib.utils import BinaryWriter
from lib.utils.writer import write_block

# all blend modes used in Supercell games
BLENDMODES = [
    None,  # "mix" by default
    None,  # something like "mix" + "multiply"
    None,  # "layer"
    "multiply",
    "screen",
    None,  # "lighten"
    None,  # "darken"
    None,  # "difference"
    "add"
]


class MovieClip(Resource, Savable):
    MOVIE_CLIP_END_FRAME_TAG = 0

    MOVIE_CLIP_FRAME_TAGS = (5, 11)
    MOVIE_CLIP_SCALING_GRID_TAG = 31
    MOVIE_CLIP_MATRIX_BANK_TAG = 41

    def __init__(self) -> None:
        super().__init__()

        self.frame_rate: int = 30
        self.binds: List[dict] = []
        self.frames: List[MovieClipFrame] = []

        self.scaling_grid: Tuple[float, float, float, float] or None = None
        self.matrix_bank_index: int = 0

        self._id_list: List[int] or None = None

    def load(self, swf, tag: int) -> None:
        self.id = swf.reader.read_ushort()

        self.frame_rate = swf.reader.read_uchar()
        frames_count = swf.reader.read_ushort()
        self.frames = [_class() for _class in [MovieClipFrame] * frames_count]

        if tag in (3, 14):
            Console.error("Tags MovieClip and MovieClip4 is unsupported! Aborting...")
            raise TypeError()

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

        if tag == 12 or tag == 35:
            for x in range(binds_count):
                blend_index = swf.reader.read_uchar() & 0x3F
                # reversed = (bind_index >> 6) & 1 # TODO: blend modes
                self.binds[x]["blend"] = BLENDMODES[blend_index]

        for x in range(binds_count):
            self.binds[x]["name"] = swf.reader.read_ascii()

        frames_loaded = 0
        frame_elements_offset = 0
        while True:
            frame_tag = swf.reader.read_uchar()
            frame_tag_length = swf.reader.read_int()

            if frame_tag == MovieClip.MOVIE_CLIP_END_FRAME_TAG:
                break

            if frame_tag in MovieClip.MOVIE_CLIP_FRAME_TAGS:
                if frame_tag == 5:
                    Console.error("Tag MovieClipFrame is unsupported! Aborting...")
                    raise TypeError()

                elements_count = self.frames[frames_loaded].load(swf)

                for x in range(elements_count):
                    self.frames[frames_loaded].elements.append(frame_elements[frame_elements_offset + x])
                frame_elements_offset += elements_count

                frames_loaded += 1
                continue

            elif frame_tag == MovieClip.MOVIE_CLIP_SCALING_GRID_TAG:
                x = swf.reader.read_twip()
                y = swf.reader.read_twip()
                width = swf.reader.read_twip()
                height = swf.reader.read_twip()
                self.scaling_grid = (x, y, width, height)
            elif frame_tag == MovieClip.MOVIE_CLIP_MATRIX_BANK_TAG:
                self.matrix_bank_index = swf.reader.read_uchar()
            else:
                Console.warning(
                    f"MovieClip {self.id} has unknown frame tag {frame_tag} with length {frame_tag_length}! Skipping..."
                )
                swf.reader.skip(frame_tag_length)

    def save(self, stream: BinaryWriter):
        stream.write_ushort(self.id)
        stream.write_uchar(self.frame_rate)
        stream.write_ushort(len(self.frames))

        frame_elements = []
        for frame in self.frames:
            for element in frame.elements:
                frame_elements.append(element)

        stream.write_int(len(frame_elements))
        for element in frame_elements:
            stream.write_ushort(element["bind"])
            stream.write_ushort(element["matrix"])
            stream.write_ushort(element["color"])

        stream.write_ushort(len(self.binds))

        for bind in self.binds:
            stream.write_ushort(self._id_list[bind["id"]])

        for bind in self.binds:
            stream.write_uchar(BLENDMODES.index(bind["blend"]) & 0x3F)

        for bind in self.binds:
            stream.write_ascii(bind["name"])

        if self.matrix_bank_index > 0:
            write_block(stream, MovieClip.MOVIE_CLIP_MATRIX_BANK_TAG, save_matrix_bank(self.matrix_bank_index))

        for frame in self.frames:
            write_block(stream, frame.get_tag(), frame.save)

        if self.scaling_grid:
            write_block(stream, MovieClip.MOVIE_CLIP_SCALING_GRID_TAG, save_scaling_grid(self.scaling_grid))

        write_block(stream, 0, None)

    # TODO: add support for tag 35 (idk where difference, but it's also used in games)
    def get_tag(self) -> int:
        return 12

    def __eq__(self, other):
        if isinstance(other, MovieClip):
            if self.frame_rate == other.frame_rate \
                    and self.binds == other.binds \
                    and self.frames == other.frames \
                    and self.scaling_grid == other.scaling_grid \
                    and self.matrix_bank_index == other.matrix_bank_index:
                return True

        return False

    def set_id_list(self, id_list):
        self._id_list = id_list


def save_scaling_grid(scaling_grid: Tuple[float, float, float, float]):
    x, y, width, height = scaling_grid

    def wrapper(stream: BinaryWriter):
        stream.write_twip(x)
        stream.write_twip(y)
        stream.write_twip(width)
        stream.write_twip(height)
    return wrapper


def save_matrix_bank(matrix_bank_index: int):
    def wrapper(stream: BinaryWriter):
        stream.write_uchar(matrix_bank_index)
    return wrapper
