from typing import List

from lib.console import Console
from lib.sc.resource import Resource
from lib.sc.savable import Savable
from lib.sc.shape.bitmap import ShapeDrawBitmapCommand
from lib.utils import BinaryWriter
from lib.utils.writer import write_block


def get_size(coords):
    left = min(x for x, _ in coords)
    top = min(y for _, y in coords)
    right = max(x for x, _ in coords)
    bottom = max(y for _, y in coords)

    return (right - left) or 1, (bottom - top) or 1


class Shape(Resource, Savable):
    SHAPE_END_COMMAND_TAG = 0

    SHAPE_DRAW_BITMAP_COMMAND_TAGS = (4, 17, 22)
    SHAPE_DRAW_COLOR_FILL_COMMAND_TAG = 6

    def __init__(self) -> None:
        super().__init__()

        self.bitmaps: List[ShapeDrawBitmapCommand] = []

    def load(self, swf, tag: int) -> None:
        self.id = swf.reader.read_ushort()

        bitmaps_count = swf.reader.read_ushort()
        self.bitmaps = [_class() for _class in [ShapeDrawBitmapCommand] * bitmaps_count]

        points_count = 4 * bitmaps_count
        if tag == 18:
            points_count = swf.reader.read_ushort()

        bitmaps_loaded = 0
        while True:
            bitmap_tag = swf.reader.read_uchar()
            bitmap_tag_length = swf.reader.read_int()

            if bitmap_tag == Shape.SHAPE_END_COMMAND_TAG:
                break

            if bitmap_tag in Shape.SHAPE_DRAW_BITMAP_COMMAND_TAGS:
                self.bitmaps[bitmaps_loaded].load(swf, bitmap_tag)
                bitmaps_loaded += 1
                continue

            elif tag == Shape.SHAPE_DRAW_COLOR_FILL_COMMAND_TAG:
                raise TypeError("Tag ShapeDrawColorFillCommand is unsupported! Aborting...")

            Console.warning(
                f"Shape {self.id} has unknown command tag {bitmap_tag} with length {bitmap_tag_length}! Skipping...")
            swf.reader.skip(bitmap_tag_length)

    def save(self, stream: BinaryWriter):
        stream.write_ushort(self.id)
        stream.write_ushort(len(self.bitmaps))

        if self.get_tag() == 18:
            # points count for an allocator
            points_count = self.get_points_count()
            stream.write_ushort(points_count)

        for bitmap in self.bitmaps:
            write_block(stream, bitmap.get_tag(), bitmap.save)

        write_block(stream, 0, None)

    def get_tag(self) -> int:
        rectangle_bitmaps_count = sum(1 if bitmap.is_rectangle else 0 for bitmap in self.bitmaps)
        is_all_rectangles = rectangle_bitmaps_count == len(self.bitmaps)

        if is_all_rectangles:
            return 2
        return 18

    def __eq__(self, other):
        if isinstance(other, Shape):
            if self.bitmaps == other.bitmaps:
                return True
        return False

    def get_points_count(self):
        return sum(bitmap.get_points_count() for bitmap in self.bitmaps)
