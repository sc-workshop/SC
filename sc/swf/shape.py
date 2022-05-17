from math import atan2, ceil, degrees

from sc.utils import BinaryWriter


class Shape:
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
        stream = BinaryWriter()

        stream.write_ushort(self.id)
        stream.write_ushort(len(self.bitmaps))

        points_count = 0
        for bitmap in self.bitmaps:
            points_count += len(bitmap.xy_coords)
        
        stream.write_ushort(points_count)
        
        for bitmap in self.bitmaps:
            tag, buffer = bitmap.save(swf)

            stream.write_uchar(tag)
            stream.write_int(len(buffer))
            stream.write(buffer)

        stream.write(bytes(5))

        return 18, stream.buffer


class ShapeDrawBitmapCommand:
    def __init__(self) -> None:
        self.texture_index: int = -1
        self.uv_coords: list = []
        self.xy_coords: list = []
    
    def load(self, swf, tag: int):
        self.texture_index = swf.reader.read_uchar()

        points_count = 4 if tag == 4 else swf.reader.read_uchar()

        for i in range(points_count):
            x = swf.reader.read_twip()
            y = swf.reader.read_twip()
            self.xy_coords.append([x, y])
        
        for i in range(points_count):
            w = swf.reader.read_ushort() / 0xFFFF * swf.textures[self.texture_index].width
            h = swf.reader.read_ushort() / 0xFFFF * swf.textures[self.texture_index].height
            
            u, v = [ceil(i) for i in [w, h]]
            if int(w) == u:
                u += 1
            if int(h) == v:
                v += 1
            
            self.uv_coords.append([u, v])
    
    def save(self, swf):
        stream = BinaryWriter()

        stream.write_uchar(self.texture_index)
        stream.write_uchar(len(self.xy_coords))

        for coord in self.xy_coords:
            x, y = coord

            stream.write_twip(x)
            stream.write_twip(y)
        
        for coord in self.uv_coords:
            u, v = coord

            stream.write_ushort(int(round((u * 0xFFFF) / swf.textures[self.texture_index].width)))
            stream.write_ushort(int(round((v * 0xFFFF) / swf.textures[self.texture_index].height)))
        
        return 22, stream.buffer


def calculate_translation(bitmap):
    def get_center(coords):
        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]

        size = len(coords)

        return sum(x_coords) / size, sum(y_coords) / size
    
    x, y = get_center(bitmap.xy_coords)

    return x, y


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

    if uv_width == 0 or uv_height == 0:
        return 1, 1, xy_width, xy_height

    return xy_width / uv_width, xy_height / uv_height, xy_width, xy_height


def calculate_rotation2(bitmap):
    def is_clockwise(points):
        sum = 0
        for x in range(len(points)):
            x1, y1 = points[(x + 1) % len(points)]
            x2, y2 = points[x]
            sum += (x1 - x2) * (y1 + y2)
        return sum < 0
    
    uv_cw = is_clockwise(bitmap.uv_coords)
    xy_cw = is_clockwise(bitmap.xy_coords)

    mirroring = not (uv_cw == xy_cw)

    mirrored_uv = bitmap.uv_coords if not mirroring else [[-coord[0], coord[1]] for coord in bitmap.uv_coords]
    mirrored_xy = bitmap.xy_coords if not mirroring else [[-coord[0], coord[1]] for coord in bitmap.xy_coords]

    dx = mirrored_xy[1][0] - mirrored_xy[0][0]
    dy = mirrored_xy[1][1] - mirrored_xy[0][1]
    du = mirrored_uv[1][0] - mirrored_uv[0][0]
    dv = mirrored_uv[1][1] - mirrored_uv[0][1]

    angle_xy = degrees(atan2(dy, dx) + 360) % 360
    angle_uv = degrees(atan2(dv, du) + 360) % 360

    angle = (angle_xy - angle_uv + 360) % 360

    nearest = round(angle / 90) * 90

    if mirroring and not uv_cw and angle not in [90, 270]:
        nearest += 180
    
    return nearest, mirroring


def calculate_rotation(bitmap):
    def is_clockwise(points):
        sum = 0
        for x in range(len(points)):
            x1, y1 = points[(x + 1) % len(points)]
            x2, y2 = points[x]
            sum += (x1 - x2) * (y1 + y2)
        return sum < 0
    
    uv_cw = is_clockwise(bitmap.uv_coords)
    xy_cw = is_clockwise(bitmap.xy_coords)

    mirroring = not (uv_cw == xy_cw)

    sheet_pos_0 = bitmap.uv_coords[0]
    sheet_pos_1 = bitmap.uv_coords[1]
    shape_pos_0 = bitmap.xy_coords[0]
    shape_pos_1 = bitmap.xy_coords[1]

    if sheet_pos_0 == sheet_pos_1:
        sheet_pos_0[0] += 1
    
    if mirroring:
        shape_pos_0[0] *= -1
        shape_pos_1[0] *= -1
    
    if sheet_pos_1[0] > sheet_pos_0[0]:
        sheet_x = 1
    elif sheet_pos_1[0] < sheet_pos_0[0]:
        sheet_x = 2
    else:
        sheet_x = 3

    if sheet_pos_1[1] < sheet_pos_0[1]:
        sheet_y = 1
    elif sheet_pos_1[1] > sheet_pos_0[1]:
        sheet_y = 2
    else:
        sheet_y = 3

    if shape_pos_1[0] > shape_pos_0[0]:
        shape_x = 1
    elif shape_pos_1[0] < shape_pos_0[0]:
        shape_x = 2
    else:
        shape_x = 3

    if shape_pos_1[1] > shape_pos_0[1]:
        shape_y = 1
    elif shape_pos_1[1] < shape_pos_0[1]:
        shape_y = 2
    else:
        shape_y = 3
    
    rotation = 0
    if sheet_x == shape_x and sheet_y == shape_y:
        rotation = 0
    elif sheet_x == 3:
        if sheet_x == shape_y:
            if sheet_y == shape_x:
                rotation = 1
            else:
                rotation = 3
        else:
            rotation = 2
    elif sheet_y == 3:
        if sheet_y == shape_x:
            if sheet_x == shape_y:
                rotation = 3
            else:
                rotation = 1
        else:
            rotation = 2
    elif sheet_x != shape_x and sheet_y != shape_y:
        rotation = 2
    elif sheet_x == sheet_y:
        if sheet_x != shape_x:
            rotation = 3
        elif sheet_y != shape_y:
            rotation = 1
    elif sheet_x != sheet_y:
        if sheet_x != shape_x:
            rotation = 1
        elif sheet_y != shape_y:
            rotation = 3

    if uv_cw == False and rotation in (1, 3):
        rotation += 2
        rotation %= 4

    return rotation * 90, mirroring
