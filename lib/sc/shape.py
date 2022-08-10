from math import ceil, degrees, radians, atan2

from lib.console import Console

from .resource import Resource
from .writable import Writable

import numpy as np
from PIL import Image, ImageDraw

from affine6p import estimate


def get_size(coords):
    left = min(x for x, _ in coords)
    top = min(y for _, y in coords)
    right = max(x for x, _  in coords)
    bottom = max(y for _, y in coords)

    return right - left or 1, bottom - top or 1


class Shape(Resource, Writable):

    SHAAPE_END_COMMAND_TAG = 0

    SHAAPE_DRAW_BITMAP_COMMAND_TAGS = (4, 17, 22)
    SHAPE_DRAW_COLOR_FILL_COMMAND_TAG = 6

    def __init__(self) -> None:
        super().__init__()

        self.bitmaps: list = []

    def load(self, swf, tag: int):
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

            if bitmap_tag == Shape.SHAAPE_END_COMMAND_TAG:
                break

            if bitmap_tag in Shape.SHAAPE_DRAW_BITMAP_COMMAND_TAGS:
                self.bitmaps[bitmaps_loaded].load(swf, bitmap_tag)
                bitmaps_loaded += 1
                continue

            elif tag == Shape.SHAPE_DRAW_COLOR_FILL_COMMAND_TAG:
                Console.error("Tag ShapeDrawColorFillCommand is unsupported! Aborting...")
                raise TypeError()

            Console.warning(f"Shape {self.id} has unknown command tag {bitmap_tag} with length {bitmap_tag_length}! Skipping...")
            swf.reader.skip(bitmap_tag_length)

    def save(self, swf):
        super().save()

        self.write_ushort(self.id)
        self.write_ushort(len(self.bitmaps))

        points_count = 0
        max_rects_count = 0
        for bitmap in self.bitmaps:
            points_count += len(bitmap.xy_coords)
            if bitmap.max_rects:
                max_rects_count += 1

        tag = 2 if max_rects_count == len(self.bitmaps) else 18

        # allocator?
        if tag == 18:
            self.write_ushort(points_count)

        for bitmap in self.bitmaps:
            tag_bitmap, buffer = bitmap.save(swf)

            self.write_uchar(tag_bitmap)
            self.write_int(len(buffer))
            self.write(buffer)

        self.write(bytes(5))  # end tag for bitmap tags array

        return tag, self.buffer


class ShapeDrawBitmapCommand(Writable):
    def __init__(self) -> None:
        self.texture_index: int = -1
        self.uv_coords: list = []
        self.xy_coords: list = []

        self.max_rects: bool = False

    def load(self, swf, tag: int):
        self.texture_index = swf.reader.read_uchar()

        self.max_rects = tag == 4
        points_count = 4 if self.max_rects else swf.reader.read_uchar()

        for i in range(points_count):
            x = swf.reader.read_twip()
            y = swf.reader.read_twip()
            self.xy_coords.append([x, y])

        for i in range(points_count):
            w = swf.reader.read_ushort()
            h = swf.reader.read_ushort()

            if tag == 22:
                w = w / 0xFFFF * swf.textures[self.texture_index].width
                h = h / 0xFFFF * swf.textures[self.texture_index].height

            u, v = [ceil(i) for i in [w, h]]

            self.uv_coords.append([u, v])

    def save(self, swf):
        super().save()

        tag = 4 if self.max_rects else 22
        points_count = 4 if self.max_rects else len(self.xy_coords)

        self.write_uchar(self.texture_index)

        if not self.max_rects:
            self.write_uchar(points_count)

        if (swf.textures[self.texture_index].mag_filter, swf.textures[self.texture_index].min_filter) == (
                "GL_NEAREST", "GL_NEAREST") and not self.max_rects:
            tag = 17

        for coord in self.xy_coords[:points_count]:
            x, y = coord

            self.write_twip(x)
            self.write_twip(y)

        for coord in self.uv_coords[:points_count]:
            u, v = coord

            if tag == 22:
                u *= 0xFFFF / swf.textures[self.texture_index].width
                v *= 0xFFFF / swf.textures[self.texture_index].height

            self.write_ushort(int(u))
            self.write_ushort(int(v))

        return tag, self.buffer
    
    def get_image(self, swf) -> Image:
        texture = swf.textures[self.texture_index]

        left = min(x for x, _ in self.uv_coords)
        top = min(y for _, y in self.uv_coords)
        right = max(x for x, _ in self.uv_coords)
        bottom = max(y for _, y in self.uv_coords)

        mask = Image.new("L", (texture.width, texture.height), 0)

        color = 255
        ImageDraw.Draw(mask).polygon([(x, y) for x, y in self.uv_coords], fill=color)

        bbox = mask.getbbox()
        if not bbox:
            if bottom - top != 0:
                for _y in range(bottom - top):
                    mask.putpixel((right - 1, top + _y - 1), color)
            elif right - left != 0:
                for _x in range(right - left):
                    mask.putpixel((left + _x - 1, bottom - 1), color)
            else:
                mask.putpixel((right - 1, bottom - 1), color)
            
            bbox = mask.getbbox()

        a, b, c, d = bbox
        if c - a - 1:
            c -= 1
        if d - b - 1:
            d -= 1

        bbox = a, b, c, d

        sprite_size = c - a, d - b
        sprite = Image.new(texture.image.mode, sprite_size)
        sprite.paste(texture.image.crop(bbox), (0, 0), mask.crop(bbox))

        rotation = self.get_rotation(nearest=True)
        sprite = sprite.rotate(rotation, expand=True)

        return sprite
    
    def get_matrix(self, custom_uv_coords: list = None, use_rotation: bool = False, use_nearest: bool = False):
        uv_coords = custom_uv_coords or self.uv_coords

        rotation = 0
        if use_rotation:
            rotation = self.get_rotation(use_nearest)

            rad = radians(rotation)

            uv_coords = [
                np.array(
                    (
                        (np.cos(rad), -np.sin(rad)),
                        (np.sin(rad), np.cos(rad))
                    )
                ).dot(point).tolist() for point in self.uv_coords
            ]

        sprite_box = []

        for idx, _ in enumerate(uv_coords):
            if idx == 0:
                sprite_box.append([0, 0])
            else:
                x_distance = uv_coords[idx][0] - uv_coords[idx - 1][0]
                y_distance = uv_coords[idx][1] - uv_coords[idx - 1][1]

                sprite_box.append([sprite_box[idx - 1][0] + x_distance,
                                   sprite_box[idx - 1][1] + y_distance])
            
            if sprite_box[idx][0] < 0:
                sprite_box = [[x - sprite_box[idx][0], y] for x, y in sprite_box]
            
            if sprite_box[idx][1] < 0:
                sprite_box = [[x, y - sprite_box[idx][1]] for x, y in sprite_box]
        
        scale_x, scale_y = get_size(sprite_box)

        if scale_x == 1:
            sprite_box = [[0, scale_y], [scale_x, scale_y], [scale_x, 0], [0, 0]]
        
        if scale_y == 1:
            sprite_box = [[scale_x, 0], [0, 0], [0, scale_y], [scale_x, scale_y]]
        
        transform = estimate(sprite_box, self.xy_coords)

        return transform, sprite_box, rotation
    
    def get_translation(self, centroid: bool = False):
        if centroid:
            x_coords = [x for x, _ in self.xy_coords]
            y_coords = [y for y, _ in self.xy_coords]

            size = len(self.xy_coords)

            x = sum(x_coords) / size
            y = sum(y_coords) / size

            return x, y
        
        left = min(x for x, _ in self.xy_coords)
        top = min(y for _, y in self.xy_coords)

        return left, top
    
    def get_rotation(self, nearest: bool = False):
        def is_clockwise(points):
            points_sum = 0
            for x in range(len(points)):
                x1, y1 = points[(x + 1) % len(points)]
                x2, y2 = points[x]
                points_sum += (x1 - x2) * (y1 + y2)
            return points_sum < 0

        uv_cw = is_clockwise(self.uv_coords)
        xy_cw = is_clockwise(self.xy_coords)

        mirroring = not (uv_cw == xy_cw)

        dx = self.xy_coords[1][0] - self.xy_coords[0][0]
        dy = self.xy_coords[1][1] - self.xy_coords[0][1]
        du = self.uv_coords[1][0] - self.uv_coords[0][0]
        dv = self.uv_coords[1][1] - self.uv_coords[0][1]

        angle_xy = degrees(atan2(dy, dx) + 360) % 360
        angle_uv = degrees(atan2(dv, du) + 360) % 360

        angle = (angle_xy - angle_uv + 360) % 360

        if mirroring:
            angle -= 180
        
        if nearest:
            angle = round(angle / 90) * 90

        return angle

    def get_scale(self):
        uv_left = min(x for x, _ in self.uv_coords)
        uv_top = min(y for _, y in self.uv_coords)
        uv_right = max(x for x, _ in self.uv_coords)
        uv_bottom = max(y for _, y in self.uv_coords)

        xy_left = min(x for x, _ in self.xy_coords)
        xy_top = min(y for _, y in self.xy_coords)
        xy_right = max(x for x, _ in self.xy_coords)
        xy_bottom = max(y for _, y in self.xy_coords)

        uv_width, uv_height = uv_right - uv_left, uv_bottom - uv_top
        xy_width, xy_height = xy_right - xy_left, xy_bottom - xy_top

        if uv_width <= 0:
            uv_width = 1
        
        if uv_height <= 0:
            uv_height = 1

        return xy_width / uv_width, xy_height / uv_height
