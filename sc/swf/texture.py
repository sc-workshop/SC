import cv2
import numpy as np


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
    "GL_UNSIGNED_BYTE",
]

PIXEL_SIZES = [
    4,
    4,
    2,
    2,
    2,
    4,
    2,
    4,
    4,
    2,
    1
]

def read_rgba8888(swf):
    r = swf.reader.read_uchar()
    g = swf.reader.read_uchar()
    b = swf.reader.read_uchar()
    a = swf.reader.read_uchar()
    return b, g, r, a

def read_rgba4444(swf):
    p = swf.reader.read_ushort()
    r = ((p >> 12) & 15) << 4
    g = ((p >> 8) & 15) << 4
    b = ((p >> 4) & 15) << 4
    a = (p & 15) << 4
    return b, g, r, a

def read_rgba5551(swf):
    p = swf.reader.read_ushort()
    r = ((p >> 11) & 31) << 3
    g = ((p >> 6) & 31) << 3
    b = ((p >> 1) & 31) << 3
    a = (p & 255) << 7
    return b, g, r, a

def read_rgb565(swf):
    p = swf.reader.read_ushort()
    r = ((p >> 11) & 31) << 3
    g = ((p >> 5) & 63) << 2
    b = (p & 31) << 3
    return b, g, r, 255

def read_la88(swf):
    a = swf.reader.read_uchar()
    l = swf.reader.read_uchar()
    return l, l, l, a

def read_l8(swf):
    l = swf.reader.read_uchar()
    return l, l, l, 255

PIXEL_READ_FUNCTIONS = {
    "GL_RGBA8": read_rgba8888,
    "GL_RGBA4": read_rgba4444,
    "GL_RGB5_A1": read_rgba5551,
    "GL_RGB565": read_rgb565,
    "GL_LUMINANCE8_ALPHA8": read_la88,
    "GL_LUMINANCE8": read_l8
}


def make_linear(texture, pixels):
    block_size = 32

    x_blocks = texture.width // block_size
    y_blocks = texture.height // block_size

    x_rest = texture.width % block_size
    y_rest = texture.height % block_size

    i = 0
    for y_block in range(y_blocks):
        for x_block in range(x_blocks):
            for y in range(block_size):
                for x in range(block_size):
                    texture.image[ y_block * block_size + y, x_block * block_size + x] = pixels[i]
                    i += 1
        
        for y in range(block_size):
            for x in range(x_rest):
                texture.image[ y_block * block_size + y, (texture.width - x_rest) + x] = pixels[i]
                i += 1
    
    for x_block in range(x_blocks):
        for y in range(y_rest):
            for x in range(block_size):
                texture.image[(texture.height - y_rest) + y, x_block * block_size + x] = pixels[i]
                i += 1
    
    for y in range(y_rest):
        for x in range(x_rest):
            texture.image[y + (texture.height - y_rest), x + (texture.width - x_rest)] = pixels[i]
            i += 1


class SWFTexture:
    def __init__(self) -> None:
        self.pixel_format: str = "GL_RGBA"
        self.pixel_internal_format: str = "GL_RGBA8"
        self.pixel_type: str = "GL_UNSIGNED_BYTE"

        self.mag_filter: str = "GL_LINEAR"
        self.min_filter: str = "GL_NEAREST"
        self.linear: bool = True
        self.downscaling: bool = True

        self.width: int = 0
        self.height: int = 0

        self.image = None
    
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
        
        self.linear = True if tag not in [27, 28, 29] else False
        self.downscaling = True if tag in [1, 16, 28, 29] else False

        self.width = swf.reader.read_ushort()
        self.height = swf.reader.read_ushort()

        if not has_external_texture:
            pixels = []
            for y in range(self.height):
                for x in range(self.width):
                    pixels.append(PIXEL_READ_FUNCTIONS[self.pixel_internal_format](swf))
            
            self.image = np.array(pixels).reshape(self.height, self.width, 4)

            if not self.linear:
                make_linear(self, pixels)
