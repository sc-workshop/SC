from lib.utils import BinaryWriter


def write_rgba8(writer: BinaryWriter, pixel):
    r, g, b, a = pixel
    writer.write_uchar(r)
    writer.write_uchar(g)
    writer.write_uchar(b)
    writer.write_uchar(a)


def write_rgba4(writer: BinaryWriter, pixel):
    r, g, b, a = pixel
    writer.write_ushort(a >> 4 | b >> 4 << 4 | g >> 4 << 8 | r >> 4 << 12)


def write_rgb5_a1(writer: BinaryWriter, pixel):
    r, g, b, a = pixel
    writer.write_ushort(a >> 7 | b >> 3 << 1 | g >> 3 << 6 | r >> 3 << 11)


def write_rgb565(writer: BinaryWriter, pixel):
    r, g, b = pixel
    writer.write_ushort(int(b >> 3 | g >> 2 << 5 | r >> 3 << 11))


def write_luminance8_alpha8(writer: BinaryWriter, pixel):
    l, a = pixel
    writer.write_ushort(l << 8 | a)


def write_luminance8(writer: BinaryWriter, pixel):
    writer.write_uchar(int(pixel))


__all__ = [
    'write_rgba8',
    'write_rgba4',
    'write_rgb5_a1',
    'write_rgb565',
    'write_luminance8_alpha8',
    'write_luminance8'
]
