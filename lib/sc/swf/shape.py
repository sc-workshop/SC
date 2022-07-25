from math import ceil, degrees, radians

import numpy as np
import cv2
import affine6p

from .writable import Writable


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

        self.write(bytes(5))  # end tag for bitmap tags array

        return tag, self.buffer

    @staticmethod
    def get_matrix(uv, xy, use_nearest=False):
        nearest = 0
        if use_nearest:
            # calculate base rotation
            try:
                rot = affine6p.estimate(uv, xy)
                rot = rot.get_rotation_x() + rot.get_rotation_y()
            except:
                rot = 0

            # getting nearest
            nearest = round(degrees(rot) / 90) * 90
            near_rad = radians(nearest)
            # rotating uv
            uv = [np.array(((np.cos(near_rad), -np.sin(near_rad)),
                            (-np.sin(near_rad), np.cos(near_rad)))).dot(point).tolist() for point in uv]


        sprite_box = []

        # rebulding mesh to corner
        for p_i, p in enumerate(uv):
            if p_i == 0:
                sprite_box.append([0, 0])
            else:
                x_distance = uv[p_i][0] - uv[p_i - 1][0]
                y_distance = uv[p_i][1] - uv[p_i - 1][1]

                sprite_box.append([sprite_box[p_i - 1][0] + x_distance,
                                   sprite_box[p_i - 1][1] + y_distance])
            if sprite_box[p_i][0] < 0:
                sprite_box = [[x - sprite_box[p_i][0], y] for x, y in sprite_box]
            if sprite_box[p_i][1] < 0:
                sprite_box = [[x, y - sprite_box[p_i][1]] for x, y in sprite_box]
        try:
            transf = affine6p.estimate(sprite_box, xy)
        except:
            return [[0,0,0], [0,0,0]], sprite_box, 0

        return transf, sprite_box, nearest

    @staticmethod
    def get_bitmap(texture, uv):
        image_box = cv2.boundingRect(np.array(uv))
        a, b, _, _ = image_box

        points = np.array(uv, dtype=np.int32)
        mask = np.zeros(texture.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)
        res = cv2.bitwise_and(texture, texture, mask=mask)

        img_w, img_h = calculate_size(uv)
        return res[b: b + int(img_h), a: a + int(img_w)]


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

            self.write_ushort(int(round(u)))
            self.write_ushort(int(round(v)))

        return tag, self.buffer


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
