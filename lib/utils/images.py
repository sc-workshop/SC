import cv2
import numpy as np


# basic stuff

CHANNLES_TABLE = {
    "GL_RGBA": 4,
    "GL_RGB": 3,
    "GL_LUMINANCE_ALPHA": 4, # OpenCV doesn't support LUMINANCE_ALPHA :(((
    "GL_LUMINANCE": 1
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

# load stuff

def read_rgba8(swf):
    r = swf.reader.read_uchar()
    g = swf.reader.read_uchar()
    b = swf.reader.read_uchar()
    a = swf.reader.read_uchar()
    return b, g, r, a

def read_rgba4(swf):
    p = swf.reader.read_ushort()
    r = ((p >> 12) & 15) << 4
    g = ((p >> 8) & 15) << 4
    b = ((p >> 4) & 15) << 4
    a = (p & 15) << 4
    return b, g, r, a

def read_rgb5_a1(swf):
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
    return b, g, r

def read_luminance8_alpha8(swf):
    a = swf.reader.read_uchar()
    l = swf.reader.read_uchar()
    return l, l, l, a

def read_luminance8(swf):
    return swf.reader.read_uchar()

PIXEL_READ_FUNCTIONS = {
    "GL_RGBA8": read_rgba8,
    "GL_RGBA4": read_rgba4,
    "GL_RGB5_A1": read_rgb5_a1,
    "GL_RGB565": read_rgb565,
    "GL_LUMINANCE8_ALPHA8": read_luminance8_alpha8,
    "GL_LUMINANCE8": read_luminance8
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
                    texture.image[y_block * block_size + y, x_block * block_size + x] = pixels[i]
                    i += 1
        
        for y in range(block_size):
            for x in range(x_rest):
                texture.image[y_block * block_size + y, (texture.width - x_rest) + x] = pixels[i]
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

# saving stuff

def write_rgba8(swf, pixel):
    b, g, r, a = int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3])
    swf.write_uchar(r)
    swf.write_uchar(g)
    swf.write_uchar(b)
    swf.write_uchar(a)

def write_rgba4(swf, pixel):
    b, g, r, a = int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3])
    swf.write_ushort(a >> 4 | b >> 4 << 4 | g >> 4 << 8 | r >> 4 << 12)

def write_rgb5_a1(swf, pixel):
    b, g, r, a = int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3])
    swf.write_ushort(a >> 7 | b >> 3 << 1 | g >> 3 << 6 | r >> 3 << 11)

def write_rgb565(swf, pixel):
    b, g, r = int(pixel[0]), int(pixel[1]), int(pixel[2])
    swf.write_ushort(int(b >> 3 | g >> 2 << 5 | r >> 3 << 11))

def write_luminance8_alpha8(swf, pixel):
    l, a = int(pixel[0]), int(pixel[3])
    swf.write_ushort(a << 8 | l)

def write_luminance8(swf, pixel):
    swf.write_uchar(int(pixel))

PIXEL_WRITE_FUNCTIONS = {
    "GL_RGBA8": write_rgba8,
    "GL_RGBA4": write_rgba4,
    "GL_RGB5_A1": write_rgb5_a1,
    "GL_RGB565": write_rgb565,
    "GL_LUMINANCE8_ALPHA8": write_luminance8_alpha8,
    "GL_LUMINANCE8": write_luminance8
}

def make_blocks(texture):
    height, width, channels = texture.image.shape

    block_size = 32

    x_blocks_count = width // block_size
    y_blocks_count = height // block_size
    x_rest = width % block_size
    y_rest = height % block_size
    
    pixels = []
    for y_block in range(y_blocks_count):
        for x_block in range(x_blocks_count):
            for y in range(block_size):
                for x in range(block_size):
                    pixels.append(texture.image[y + (y_block * block_size), x + (x_block * block_size)])

        for y in range(block_size):
            for x in range(x_rest):
                pixels.append(texture.image[y + (y_block * block_size), x + (width - x_rest)])

    for x_block in range(width // block_size):
        for y in range(y_rest):
            for x in range(block_size):
                pixels.append(texture.image[y + (height - y_rest), x + (x_block * block_size)])

    for y in range(y_rest):
        for x in range(x_rest):
                pixels.append(texture.image[y + (height - y_rest), x + (width - x_rest)])
    
    texture.image = np.array(pixels).reshape(height, width, channels)

# mainly used functions

def load_image(texture, swf):
    pixels = []
    for y in range(texture.height):
        for x in range(texture.width):
            pixels.append(PIXEL_READ_FUNCTIONS[texture.pixel_internal_format](swf))
    
    texture.image = np.array(pixels, dtype=np.uint8).reshape(texture.height, texture.width, CHANNLES_TABLE[texture.pixel_format])
    texture.channels = texture.image.shape[2]

    if not texture.linear:
        make_linear(texture, pixels)


def save_image(texture):
    if not texture.linear:
        make_blocks(texture)

    for y in range(texture.height):
        for x in range(texture.width):
            PIXEL_WRITE_FUNCTIONS[texture.pixel_internal_format](texture, texture.image[y, x])
