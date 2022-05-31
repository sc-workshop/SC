from math import atan2, ceil, degrees

from .writable import Writable


class Shape(Writable):
    def __init__(self) -> None:
        self.id: int = -1

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

            if bitmap_tag == 0:
                break

            if bitmap_tag in [4, 17, 22]:
                self.bitmaps[bitmaps_loaded].load(swf, bitmap_tag)
                bitmaps_loaded += 1
                continue

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

        self.write(bytes(5)) # end tag for bitmap tags array

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

        if (swf.textures[self.texture_index].mag_filter, swf.textures[self.texture_index].min_filter) == ("GL_NEAREST", "GL_NEAREST") and not self.max_rects:
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

            self.write_ushort(int(round(u)))
            self.write_ushort(int(round(v)))
        
        return tag, self.buffer

def get_center(coords):
    x_coords = [coord[0] for coord in coords]
    y_coords = [coord[1] for coord in coords]

    size = len(coords)

    return sum(x_coords) / size, sum(y_coords) / size

def calculate_scale(uv_coords, xy_coords):
    uv_left = min(coord[0] for coord in uv_coords)
    uv_top = min(coord[1] for coord in uv_coords)
    uv_right = max(coord[0] for coord in uv_coords)
    uv_bottom = max(coord[1] for coord in uv_coords)

    xy_left = min(coord[0] for coord in xy_coords)
    xy_top = min(coord[1] for coord in xy_coords)
    xy_right = max(coord[0] for coord in xy_coords)
    xy_bottom = max(coord[1] for coord in xy_coords)

    uv_width, uv_height = uv_right - uv_left, uv_bottom - uv_top
    xy_width, xy_height = xy_right - xy_left, xy_bottom - xy_top

    if uv_width == 0: uv_width = 1
    if uv_height == 0: uv_height = 1

    return xy_width / uv_width, xy_height / uv_height, xy_width, xy_height


def calculate_rotation(uv_coords, xy_coords):
    def is_clockwise(points):
        sum = 0
        for x in range(len(points)):
            x1, y1 = points[(x + 1) % len(points)]
            x2, y2 = points[x]
            sum += (x1 - x2) * (y1 + y2)
        return sum < 0
    
    uv_cw = is_clockwise(uv_coords)
    xy_cw = is_clockwise(xy_coords)

    mirroring = not (uv_cw == xy_cw)

    mirrored_uv = uv_coords if not mirroring else [[-coord[0], coord[1]] for coord in uv_coords]
    mirrored_xy = xy_coords if not mirroring else [[coord[0], coord[1]] for coord in xy_coords]

    dx = mirrored_xy[1][0] - mirrored_xy[0][0]
    dy = mirrored_xy[1][1] - mirrored_xy[0][1]
    du = mirrored_uv[1][0] - mirrored_uv[0][0]
    dv = mirrored_uv[1][1] - mirrored_uv[0][1]

    angle_xy = degrees(atan2(dy, dx) + 360) % 360
    angle_uv = degrees(atan2(dv, du) + 360) % 360

    angle = round((angle_xy - angle_uv + 360) % 360)

    nearest = round(angle / 90) * 90

    if not uv_cw:
        if mirroring:
            if angle in [90, 270]:
                nearest += 180

    return nearest, mirroring
