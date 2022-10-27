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


__all__ = [
    'read_rgba8',
    'read_rgba4',
    'read_rgb5_a1',
    'read_rgb565',
    'read_luminance8_alpha8',
    'read_luminance8'
]
