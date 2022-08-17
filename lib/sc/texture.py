from .writable import Writable

from PIL import Image

from lib.console import Console


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

def read_rgba8(swf):
    r = swf.reader.read_uchar()
    g = swf.reader.read_uchar()
    b = swf.reader.read_uchar()
    a = swf.reader.read_uchar()
    return r, g, b, a


def read_rgba4(swf):
    p = swf.reader.read_ushort()
    r = ((p >> 12) & 15) << 4
    g = ((p >> 8) & 15) << 4
    b = ((p >> 4) & 15) << 4
    a = (p & 15) << 4
    return r, g, b, a


def read_rgb5_a1(swf):
    p = swf.reader.read_ushort()
    r = ((p >> 11) & 31) << 3
    g = ((p >> 6) & 31) << 3
    b = ((p >> 1) & 31) << 3
    a = (p & 255) << 7
    return r, g, b, a


def read_rgb565(swf):
    p = swf.reader.read_ushort()
    r = ((p >> 11) & 31) << 3
    g = ((p >> 5) & 63) << 2
    b = (p & 31) << 3
    return r, g, b


def read_luminance8_alpha8(swf):
    a = swf.reader.read_uchar()
    l = swf.reader.read_uchar()
    return l, a


def read_luminance8(swf):
    return swf.reader.read_uchar()


def write_rgba8(swf, pixel):
    r, g, b, a = pixel
    swf.write_uchar(r)
    swf.write_uchar(g)
    swf.write_uchar(b)
    swf.write_uchar(a)


def write_rgba4(swf, pixel):
    r, g, b, a = pixel
    swf.write_ushort(a >> 4 | b >> 4 << 4 | g >> 4 << 8 | r >> 4 << 12)


def write_rgb5_a1(swf, pixel):
    r, g, b, a = pixel
    swf.write_ushort(a >> 7 | b >> 3 << 1 | g >> 3 << 6 | r >> 3 << 11)


def write_rgb565(swf, pixel):
    r, g, b = pixel
    swf.write_ushort(int(b >> 3 | g >> 2 << 5 | r >> 3 << 11))


def write_luminance8_alpha8(swf, pixel):
    l, a = pixel
    swf.write_ushort(l << 8 | a)


def write_luminance8(swf, pixel):
    swf.write_uchar(int(pixel))


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


class SWFTexture(Writable):
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

        self.image: Image = None

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

        self.linear = tag in [27, 28, 29]
        self.downscaling = tag in [1, 16, 28, 29]

        self.width = swf.reader.read_ushort()
        self.height = swf.reader.read_ushort()

        if not has_external_texture:
            Console.info(
                f"SWFTexture: {self.width}x{self.height} - Format: {self.pixel_type} {self.pixel_format} {self.pixel_internal_format}")

            self.image = Image.new(MODES_TABLE[self.pixel_format], (self.width, self.height))
            loaded = self.image.load()

            self.channels = CHANNLES_TABLE[self.image.mode]

            read_pixel = PIXEL_READ_FUNCTIONS[self.pixel_internal_format]

            if not self.linear:
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

    def save(self, has_external_texture: bool):
        super().save()

        if self.image is not None:
            self.channels = CHANNLES_TABLE[self.image.mode]
            self.width, self.height = self.image.size

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

        pixel_type_index = PIXEL_INTERNAL_FORMATS.index(self.pixel_internal_format)

        tag = 1
        if (self.mag_filter, self.min_filter) == ("GL_LINEAR", "GL_NEAREST"):
            if self.linear:
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

        self.write_uchar(pixel_type_index)

        self.write_ushort(self.width)
        self.write_ushort(self.height)

        Console.info(
            f"SWFTexture: {self.width}x{self.height} - Format: {self.pixel_type} {self.pixel_format} {self.pixel_internal_format}")

        if not has_external_texture:
            loaded = self.image.load()

            write_pixel = PIXEL_WRITE_FUNCTIONS[self.pixel_internal_format]

            if self.linear:
                loaded_clone = self.image.copy().load()

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
                    write_pixel(self, loaded[x, y])

            print()

        return tag, self.buffer
