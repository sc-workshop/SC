from PIL import Image

from lib.console import Console
from lib.sc.savable import Savable
from lib.sc.texture.read_functions import *
from lib.sc.texture.write_functions import *
from lib.utils import BinaryWriter

PACKER_FILTER_TABLE = {
    "LINEAR": "GL_LINEAR",
    "NEAREST": "GL_NEAREST",
    "MIPMAP": "GL_LINEAR_MIPMAP_NEAREST"
}

PACKER_PIXEL_TYPES = [
    "RGBA8888",
    "BGRA8888",
    "RGBA4444",
    "RGBA5551",
    "RGB565",
    "RGBA8888",
    "ALPHA_INTENSITY",
    "RGBA8888",
    "RGBA8888",
    "ALPHA"
]

MODES_TABLE = {
    "GL_RGBA": "RGBA",
    "GL_RGB": "RGB",
    "GL_LUMINANCE_ALPHA": "LA",
    "GL_LUMINANCE": "L"
}

CHANNLES_TABLE = {
    "RGBA": 4,
    "RGB": 3,
    "LA": 2,
    "L": 1
}

PIXEL_TYPES = [
    "GL_UNSIGNED_BYTE",
    "GL_UNSIGNED_BYTE",
    "GL_UNSIGNED_SHORT_4_4_4_4",
    "GL_UNSIGNED_SHORT_5_5_5_1",
    "GL_UNSIGNED_SHORT_5_6_5",
    "GL_UNSIGNED_BYTE",
    "GL_UNSIGNED_BYTE",
    "GL_UNSIGNED_BYTE",
    "GL_UNSIGNED_BYTE",
    "GL_UNSIGNED_SHORT_4_4_4_4",
    "GL_UNSIGNED_BYTE"
]

PIXEL_FORMATS = [
    "GL_RGBA",
    "GL_RGBA",
    "GL_RGBA",
    "GL_RGBA",
    "GL_RGB",
    "GL_RGBA",
    "GL_LUMINANCE_ALPHA",
    "GL_RGBA",
    "GL_RGBA",
    "GL_RGBA",
    "GL_LUMINANCE"
]

PIXEL_INTERNAL_FORMATS = [
    "GL_RGBA8",
    "GL_RGBA8",
    "GL_RGBA4",
    "GL_RGB5_A1",
    "GL_RGB565",
    "GL_RGBA8",
    "GL_LUMINANCE8_ALPHA8",
    "GL_RGBA8",
    "GL_RGBA8",
    "GL_RGBA4",
    "GL_LUMINANCE8"
]

PIXEL_READ_FUNCTIONS = {
    "GL_RGBA8": read_rgba8,
    "GL_RGBA4": read_rgba4,
    "GL_RGB5_A1": read_rgb5_a1,
    "GL_RGB565": read_rgb565,
    "GL_LUMINANCE8_ALPHA8": read_luminance8_alpha8,
    "GL_LUMINANCE8": read_luminance8
}

PIXEL_WRITE_FUNCTIONS = {
    "GL_RGBA8": write_rgba8,
    "GL_RGBA4": write_rgba4,
    "GL_RGB5_A1": write_rgb5_a1,
    "GL_RGB565": write_rgb565,
    "GL_LUMINANCE8_ALPHA8": write_luminance8_alpha8,
    "GL_LUMINANCE8": write_luminance8
}


class SWFTexture(Savable):
    def __init__(self) -> None:
        self.channels: int = 4

        self.pixel_format: str = "GL_RGBA"
        self.pixel_internal_format: str = "GL_RGBA8"
        self.pixel_type: str = "GL_UNSIGNED_BYTE"

        self.mag_filter: str = "GL_LINEAR"
        self.min_filter: str = "GL_NEAREST"

        self.linear: bool = True
        self.downscaling: bool = True

        self.width: int = 0
        self.height: int = 0

        self._image: Image = None
        self._has_external_texture: bool = False

    def load(self, swf, tag: int, has_external_texture: bool):
        pixel_type_index = swf.reader.read_uchar()

        self.pixel_format = PIXEL_FORMATS[pixel_type_index]
        self.pixel_internal_format = PIXEL_INTERNAL_FORMATS[pixel_type_index]
        self.pixel_type = PIXEL_TYPES[pixel_type_index]

        self.mag_filter = "GL_LINEAR"
        self.min_filter = "GL_NEAREST"
        if tag in [16, 19, 29]:
            self.mag_filter = "GL_LINEAR"
            self.min_filter = "GL_LINEAR_MIPMAP_NEAREST"
        elif tag == 34:
            self.mag_filter = "GL_NEAREST"
            self.min_filter = "GL_NEAREST"

        self.linear = tag not in [27, 28, 29]
        self.downscaling = tag in [1, 16, 28, 29]

        self.width = swf.reader.read_ushort()
        self.height = swf.reader.read_ushort()

        if not has_external_texture:
            Console.info(
                f"SWFTexture: {self.width}x{self.height} - Format: {self.pixel_type} {self.pixel_format} {self.pixel_internal_format}")

            self._image = Image.new(MODES_TABLE[self.pixel_format], (self.width, self.height))
            loaded = self._image.load()

            self.channels = CHANNLES_TABLE[self._image.mode]

            read_pixel = PIXEL_READ_FUNCTIONS[self.pixel_internal_format]

            if self.linear:
                for y in range(self.height):
                    for x in range(self.width):
                        loaded[x, y] = read_pixel(swf)

                    Console.progress_bar("Loading texture data...", y, self.height)
                print()

            else:
                block_size = 32

                x_blocks = self.width // block_size
                y_blocks = self.height // block_size

                for y_block in range(y_blocks + 1):
                    for x_block in range(x_blocks + 1):
                        for y in range(block_size):
                            pixel_y = (y_block * block_size) + y

                            if pixel_y >= self.height:
                                break

                            for x in range(block_size):
                                pixel_x = (x_block * block_size) + x

                                if pixel_x >= self.width:
                                    break

                                loaded[pixel_x, pixel_y] = read_pixel(swf)

                    Console.progress_bar("Loading splitted texture data...", y_block, y_blocks + 1)
            print()

    def save(self, stream: BinaryWriter) -> None:
        pixel_type_index = PIXEL_INTERNAL_FORMATS.index(self.pixel_internal_format)

        stream.write_uchar(pixel_type_index)

        stream.write_ushort(self.width)
        stream.write_ushort(self.height)

        Console.info(
            f"SWFTexture: {self.width}x{self.height} - "
            f"Format: {self.pixel_type} {self.pixel_format} {self.pixel_internal_format}"
        )

        if not self._has_external_texture:
            loaded = self._image.load()

            write_pixel = PIXEL_WRITE_FUNCTIONS[self.pixel_internal_format]

            if not self.linear:
                loaded_clone = self._image.copy().load()

                def add_pixel(pixel: tuple):
                    loaded[pixel_index % self.width, pixel_index // self.width] = pixel

                block_size = 32

                x_blocks = self.width // block_size
                y_blocks = self.height // block_size

                pixel_index = 0
                for y_block in range(y_blocks + 1):
                    for x_block in range(x_blocks + 1):
                        for y in range(block_size):
                            pixel_y = (y_block * block_size) + y

                            if pixel_y >= self.height:
                                break

                            for x in range(block_size):
                                pixel_x = (x_block * block_size) + x

                                if pixel_x >= self.width:
                                    break

                                add_pixel(loaded_clone[pixel_x, pixel_y])
                                pixel_index += 1

                loaded = loaded_clone

            for y in range(self.height):
                Console.progress_bar("Writing texture data...", y, self.height)
                for x in range(self.width):
                    write_pixel(stream, loaded[x, y])

            print()

    def get_tag(self) -> int:
        tag = 1
        if (self.mag_filter, self.min_filter) == ("GL_LINEAR", "GL_NEAREST"):
            if not self.linear:
                tag = 27 if not self.downscaling else 28
            else:
                tag = 24 if not self.downscaling else 1

        if (self.mag_filter, self.min_filter) == ("GL_LINEAR", "GL_LINEAR_MIPMAP_NEAREST"):
            if not self.linear and not self.downscaling:
                tag = 29
            else:
                tag = 19 if not self.downscaling else 16

        if (self.mag_filter, self.min_filter) == ("GL_NEAREST", "GL_NEAREST"):
            tag = 34
        return tag

    def set_has_external_texture(self, has_external_texture: bool):
        self._has_external_texture = has_external_texture

    def get_image(self):
        return self._image

    def set_image(self, img: Image):
        self._image = img

        self.channels = CHANNLES_TABLE[self._image.mode]
        self.width, self.height = self._image.size

        if self.channels == 4:
            self.pixel_format = "GL_RGBA"

            if self.pixel_type == "GL_UNSIGNED_BYTE":
                self.pixel_internal_format = "GL_RGBA8"

            elif self.pixel_type == "GL_UNSIGNED_SHORT_4_4_4_4":
                self.pixel_internal_format = "GL_RGBA4"

            else:
                self.pixel_internal_format = "GL_RGB5_A1"

        elif self.channels == 3:
            self.pixel_format = "GL_RGB"
            self.pixel_type = "GL_UNSIGNED_SHORT_5_6_5"
            self.pixel_internal_format = "GL_RGB565"

        elif self.channels == 2:
            self.pixel_format = "GL_LUMINANCE_ALPHA"
            self.pixel_type = "GL_UNSIGNED_BYTE"
            self.pixel_internal_format = "GL_LUMINANCE8_ALPHA8"

        else:
            self.pixel_format = "GL_LUMINANCE"
            self.pixel_type = "GL_UNSIGNED_BYTE"
            self.pixel_internal_format = "GL_LUMINANCE8"


def save_texture(texture: SWFTexture, has_external_texture: bool):
    def wrapper(stream: BinaryWriter):
        texture.set_has_external_texture(has_external_texture)
        texture.save(stream)

    return wrapper
