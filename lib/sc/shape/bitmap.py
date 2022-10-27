from math import ceil, radians, sin, cos, atan2, degrees
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw
from affine6p import estimate

from lib.sc.texture import SWFTexture
from lib.sc.savable import Savable
from lib.utils import BinaryWriter


class ShapeDrawBitmapCommand(Savable):
    def __init__(self) -> None:
        self.texture_index: int = -1
        self.texture: SWFTexture or None = None
        self.uv_coordinates: List[Tuple[int, int]] = []
        self.xy_coordinates: List[Tuple[int, int]] = []

        self.is_rectangle: bool = False

    def load(self, swf, tag: int):
        self.texture_index = swf.reader.read_uchar()
        self.texture = swf.textures[self.texture_index]

        self.is_rectangle = tag == 4
        points_count = 4 if self.is_rectangle else swf.reader.read_uchar()

        for i in range(points_count):
            x = swf.reader.read_twip()
            y = swf.reader.read_twip()
            self.xy_coordinates.append((x, y))

        for i in range(points_count):
            w = swf.reader.read_ushort()
            h = swf.reader.read_ushort()

            if tag == 22:
                w = w / 0xFFFF * self.texture.width
                h = h / 0xFFFF * self.texture.height

            u, v = [ceil(i) for i in [w, h]]

            self.uv_coordinates.append((u, v))

    def save(self, stream: BinaryWriter):
        points_count = self.get_points_count()

        stream.write_uchar(self.texture_index)

        if not self.is_rectangle:
            stream.write_uchar(points_count)

        for coord in self.xy_coordinates[:points_count]:
            x, y = coord

            stream.write_twip(x)
            stream.write_twip(y)

        tag = self.get_tag()
        for coord in self.uv_coordinates[:points_count]:
            u, v = coord

            if tag == 22:
                u *= 0xFFFF / self.texture.width
                v *= 0xFFFF / self.texture.height

            stream.write_ushort(int(u))
            stream.write_ushort(int(v))

    def get_tag(self) -> int:
        if self.is_rectangle:
            return 4

        mag_filter = self.texture.mag_filter
        min_filter = self.texture.min_filter
        if mag_filter == "GL_NEAREST" and min_filter == "GL_NEAREST":
            return 17

        return 22

    def get_image(self, swf) -> Image:
        texture = swf.textures[self.texture_index]
        image = texture.get_image()

        w, h = self.get_size(self.uv_coordinates)
        if w == 0:
            w = 1
        if h == 0:
            h = 1

        if w + h == 2:
            x, y = self.uv_coordinates[-1]
            return Image.new(texture.image.mode, (1, 1), texture.image.getpixel((x, y)))

        mask = Image.new("L", (texture.width, texture.height), 0)

        color = 255
        ImageDraw.Draw(mask).polygon([(x, y) for x, y in self.uv_coordinates], fill=color)

        left = min(x for x, _ in self.uv_coordinates)
        top = min(y for _, y in self.uv_coordinates)
        right = max(x for x, _ in self.uv_coordinates)
        bottom = max(y for _, y in self.uv_coordinates)

        if w == 1:
            right += 1
        if h == 1:
            bottom += 1

        bbox = left, top, right, bottom

        sprite = Image.new(image.mode, (w, h))
        sprite.paste(image.crop(bbox), (0, 0), mask.crop(bbox))

        return sprite

    def get_matrix(self, custom_uv_coords: list = None, use_nearest: bool = False):
        uv_coordinates = custom_uv_coords or self.uv_coordinates

        rotation = 0
        mirroring = False
        if use_nearest:
            rotation, mirroring = self.get_rotation(use_nearest)

            rad = radians(rotation)

            uv_coordinates = [
                np.array(
                    (
                        (np.cos(rad), -np.sin(rad)),
                        (np.sin(rad), np.cos(rad))
                    )
                ).dot(point).tolist() for point in self.uv_coordinates
            ]

            uv_coordinates = [(round(x), round(y)) for x, y in uv_coordinates]

            if mirroring:
                uv_coordinates = [(-x, y) for x, y, in uv_coordinates]

        sprite_box: List[Tuple[int, int]] = []

        for idx in range(len(uv_coordinates)):
            if idx == 0:
                sprite_box.append((0, 0))
            else:
                x_distance = uv_coordinates[idx][0] - uv_coordinates[idx - 1][0]
                y_distance = uv_coordinates[idx][1] - uv_coordinates[idx - 1][1]

                sprite_box.append((round(sprite_box[idx - 1][0] + x_distance, 3),
                                   round(sprite_box[idx - 1][1] + y_distance, 3)))

            if sprite_box[idx][0] < 0:
                sprite_box = [(x - sprite_box[idx][0], y) for x, y in sprite_box]

            if sprite_box[idx][1] < 0:
                sprite_box = [(x, y - sprite_box[idx][1]) for x, y in sprite_box]

        w, h = self.get_size(uv_coordinates)
        if w == 0 or h == 0:
            sprite_box = self.get_right_uv(False, sprite_box)

        transform = estimate(sprite_box, self.xy_coordinates)

        return transform, sprite_box, rotation, mirroring

    def get_points_count(self):
        return 4 if self.is_rectangle else len(self.xy_coordinates)

    @staticmethod
    def scale_around(point: Tuple[int, int], center: Tuple[int, int], scale: Tuple[int, int]) -> (int, int):
        c_x, c_y = center
        x, y = point
        sx, sy = scale
        return round(((x - c_x) * sx)), round(((y - c_y) * sy))

    @staticmethod
    def move_by_angle(point: Tuple[int, int], angle: float, distance: float) -> (int, int):
        """

        :param point:
        :param angle: angle, measured in radians
        :param distance:
        :return:
        """
        x, y = point

        x += distance * sin(angle)
        y += distance * cos(angle)

        return round(x) or 0, round(y) or 0

    @staticmethod
    def find_angle(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculates an angle between two points.

        :param point1: first point
        :param point2: second point
        :return: angle, measured in degrees
        """
        x1, y1 = point1
        x2, y2 = point2
        dx = x2 - x1
        dy = y2 - y1
        rads = atan2(-dy, dx)
        return degrees(rads)

    def get_right_uv(self, inside: bool, custom: List[Tuple[int, int]] = None):
        coordinates = custom if custom is not None else self.uv_coordinates

        res = coordinates.copy()
        w, h = ShapeDrawBitmapCommand.get_size(coordinates)

        if not inside and w == 0 or h == 0:
            unique_points = [tuple(x) for x in set(tuple(x) for x in coordinates)]
            for index, point in enumerate(unique_points):
                if coordinates[0] == coordinates[1]:
                    point_idx = index + 1
                else:
                    point_idx = 3 - (list(reversed(res)).index(point))

                res[point_idx] = (res[point_idx][0] + (1 if w == 0 else 0),
                                  res[point_idx][1] + (1 if h == 0 else 0))

            return res
        else:
            if len(coordinates) <= 4:
                w_m = (w + 2) if inside else (w - 2 if w > 2 else 0)
                h_m = (h + 2) if inside else (h - 2 if h > 2 else 0)

                c_x, c_y = [sum([x for x, _ in coordinates]) / len(coordinates), sum([y for _, y in coordinates]) / len(coordinates)]

                return [[round((w_m / w) * (x - c_x) + c_x), round((h_m / h) * (y - c_y) + c_y)] for x, y in coordinates]

            for i, point in enumerate(coordinates):
                if i == 0:
                    last = len(coordinates) - 1
                else:
                    last = i - 1

                angle = radians(self.find_angle(coordinates[last], coordinates[i]) - 45)

                res[i] = self.move_by_angle(coordinates[i], angle, -1 if inside else 1)

            return res

    def get_translation(self, centroid: bool = False):
        if centroid:
            x_sum = sum(x for x, _ in self.xy_coordinates)
            y_sum = sum(y for y, _ in self.xy_coordinates)

            x = x_sum / len(self.xy_coordinates)
            y = y_sum / len(self.xy_coordinates)

            return x, y

        left = min(x for x, _ in self.xy_coordinates)
        top = min(y for _, y in self.xy_coordinates)

        return left, top

    def get_rotation(self, nearest: bool = False):
        def is_clockwise(points):
            points_sum = 0
            for x in range(len(points)):
                x1, y1 = points[(x + 1) % len(points)]
                x2, y2 = points[x]
                points_sum += (x1 - x2) * (y1 + y2)
            return points_sum > 0

        uv_cw = is_clockwise(self.uv_coordinates)
        xy_cw = is_clockwise(self.xy_coordinates)

        mirroring = not (uv_cw == xy_cw)

        dx = self.xy_coordinates[1][0] - self.xy_coordinates[0][0]
        dy = self.xy_coordinates[1][1] - self.xy_coordinates[0][1]
        du = self.uv_coordinates[1][0] - self.uv_coordinates[0][0]
        dv = self.uv_coordinates[1][1] - self.uv_coordinates[0][1]

        angle_xy = degrees(atan2(dy, dx)) % 360
        angle_uv = degrees(atan2(dv, du)) % 360

        angle = (angle_xy - angle_uv + 360) % 360

        if mirroring:
            angle -= 180

        if nearest:
            angle = round(angle / 90) * 90

        return angle, mirroring

    @staticmethod
    def get_size(coordinates: List[Tuple[int, int] or List[int, int]]):
        left = min(coord[0] for coord in coordinates)
        top = min(coord[1] for coord in coordinates)
        right = max(coord[0] for coord in coordinates)
        bottom = max(coord[1] for coord in coordinates)

        return right - left, bottom - top

    def get_scale(self):
        uv_x, uv_y = self.get_size(self.uv_coordinates)
        xy_x, xy_y = self.get_size(self.xy_coordinates)

        return uv_x / xy_x, uv_y / xy_y

    def __eq__(self, other):
        if self.is_rectangle == other.is_rectangle \
                and self.uv_coordinates == other.uv_coordinates \
                and self.xy_coordinates == other.xy_coordinates \
                and self.texture_index == other.texture_index:
            return True
        return False
