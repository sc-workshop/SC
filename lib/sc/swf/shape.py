from math import atan2, ceil, degrees, radians

import numpy as np
import cv2
from scipy.ndimage import rotate

from .writable import Writable
from lib.utils.affinetransform import AffineTransform


class Shape(Writable):
    def __init__(self) -> None:
        self.id: int = -1

        self.bitmaps: list = []
    
    def load(self, swf, tag: int):
        self.id = swf.reader.read_ushort()

        swf.shapes_ids.append(self.id)

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

def get_bounding_box(coords):
    left = min(coord[0] for coord in coords)
    top = min(coord[1] for coord in coords)
    right = max(coord[0] for coord in coords)
    bottom = max(coord[1] for coord in coords)

    return [[left, top], [left, bottom], [right, bottom], [right, top]]

def calculate_scale(uv_coords, xy_coords):
    uv_width, uv_height = calculate_size(uv_coords)
    xy_width, xy_height = calculate_size(xy_coords)

    return xy_width / uv_width, xy_height / uv_height

def calculate_size(coords):
    left = min(coord[0] for coord in coords)
    top = min(coord[1] for coord in coords)
    right = max(coord[0] for coord in coords)
    bottom = max(coord[1] for coord in coords)

    return right - left or 1, bottom - top or 1

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

    angle = (angle_xy - angle_uv + 360) % 360

    nearest = round(angle / 90) * 90

    if nearest in [90, 270] and mirroring:
        angle += 180

    return angle, nearest, mirroring

def get_matrix(uv, xy, use_nearest = False, raw_data = False):
    def rotate(points, angle):
        rotate_matrix = np.array(((np.cos(angle), np.sin(angle)),
                                (-np.sin(angle), np.cos(angle))))

        return [[round(p, 3) for p in rotate_matrix.dot(vec).tolist()] for vec in points]
    at = AffineTransform()

    rotation, nearest, mirroring = calculate_rotation(uv, xy)
    nearest_rad = radians(-nearest)
    rad_rot = radians(-rotation)
    if use_nearest: rad_rot -= nearest_rad

    sprite_mesh = rotate(uv, nearest_rad) if use_nearest else uv
    sprite_box = []

    # rebulding mesh to corner
    for p_i, p in enumerate(sprite_mesh):
        if p_i == 0:
            sprite_box.append([0, 0])
        else:
            x_distance = sprite_mesh[p_i][0] - sprite_mesh[p_i - 1][0]
            y_distance = sprite_mesh[p_i][1] - sprite_mesh[p_i - 1][1]

            sprite_box.append([sprite_box[p_i - 1][0] + x_distance,
                               sprite_box[p_i - 1][1] + y_distance])
        if sprite_box[p_i][0] < 0:
            sprite_box = [[x - sprite_box[p_i][0], y] for x, y in sprite_box]
        if sprite_box[p_i][1] < 0:
            sprite_box = [[x, y - sprite_box[p_i][1]] for x, y in sprite_box]

    sx, sy = calculate_scale(sprite_box, rotate(xy, -rad_rot))  # calculate scale
    # TODO skew

    at.scale(sx, sy)  # apply scale
    sprite = [[round(x * sx, 3), round(y * sy, 3)] for x, y in sprite_box]

    if mirroring:
        at.scale(-1, 1)
        sprite = [[-x, y] for x, y in sprite]

    # rotating bounding box and matrix
    sprite = rotate(sprite, rad_rot)

    at.rotate(rad_rot)  # apply rotation

    s_center_x, s_center_y = get_center(get_bounding_box(sprite))
    xy_center_x, xy_center_y = get_center(get_bounding_box(xy))

    translition_x = round(xy_center_x - s_center_x)
    translition_y = round(xy_center_y - s_center_y)

    at.ty = translition_x
    at.tx = translition_y

    if raw_data:
        return (rotation, mirroring), (sx, sy), (translition_x, translition_y)

    return at.get_matrix(), sprite_box, nearest if use_nearest else 0,

def get_bitmap(textures, uv, tex_id):
    image_box = cv2.boundingRect(np.array(uv))
    a, b, _, _ = image_box

    texture = textures[tex_id].image
    points = np.array(uv, dtype=np.int32)
    mask = np.zeros(texture.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)
    res = cv2.bitwise_and(texture, texture, mask=mask)

    img_w, img_h = calculate_size(uv)
    return res[b: b + int(img_h), a: a + int(img_w)]

def render_shape(shape, textures):
    def add(back, fore, x, y):
        rows, cols, channels = fore.shape
        trans_indices = fore[..., 3] != 0
        overlay_copy = back[y:y + rows, x:x + cols]
        overlay_copy[trans_indices] = fore[trans_indices]
        back[y:y + rows, x:x + cols] = overlay_copy

    box = get_bounding_box([p for bitmap in shape.bitmaps for p in bitmap.xy_coords])
    min_x = min([p[0] for p in box])
    min_y = min([p[1] for p in box])
    box = [[x - min_x, y - min_y] for x, y in box]

    width = int(max([p[0] for p in box]))
    x_offset = ceil(width/2)
    height = int(max([p[1] for p in box]))
    y_offset = ceil(height/2)

    img = np.zeros((height, width, 4), np.uint8)
    img[:,:] = (255, 0, 0, 0)

    for bitmap in reversed(shape.bitmaps):
        (rotation, mirror), (scale_x, scale_y), (tr_y, tr_x) = get_matrix(bitmap.uv_coords, bitmap.xy_coords, raw_data=True)

        bitmap_image = get_bitmap(textures, bitmap.uv_coords, bitmap.texture_index)

        bitmap_image = rotate(bitmap_image, rotation)
        if mirror:
            bitmap_image = cv2.flip(bitmap_image, 1)

        bitmap_width = int(bitmap_image.shape[1] * scale_x)
        bitmap_height = int(bitmap_image.shape[0] * scale_y)
        if tr_x < 0:
            tr_x = -tr_x * 2
        if tr_y < 0:
            tr_y = -tr_y * 2

        bitmap_image = cv2.resize(bitmap_image, (bitmap_width, bitmap_height))
        add(img, bitmap_image, x_offset - tr_x, y_offset - tr_y)


    return img
