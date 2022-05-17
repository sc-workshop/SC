import os

import cv2
import numpy as np

from zlib import compress, decompress

from sc.utils import BinaryReader, BinaryWriter


class Bitmap:
    def save(self, image):
        width, height, channels = image.shape

        image_binary = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = image[x, y]
                image_binary.append(r << 24 | g << 16 | b << 8 | a)

        image_binary = compress(np.array(image_binary, dtype="<i").tobytes())[2:]

        stream = BinaryWriter()

        stream.write_ushort((height + width) * 2)
        stream.write_ushort(width)
        stream.write_ushort(height)
        stream.write_int(0)
        stream.write_int(width * 20)
        stream.write_int(0)
        stream.write_int(height * 20)
        stream.write_uchar(1)
        stream.write_uchar(1)
        stream.write_ushort(2)
        stream.write_ushort(376)
        
        if len(image_binary) < 2048:
            stream.write_ushort(len(image_binary))
            return b"\x03\x05" + stream.buffer + image_binary + b"\x00\x00"
        
        sliced_binary = [image_binary[i:i+2048] for i in range(0, len(image_binary), 2048)]
        for sliced in sliced_binary:
            stream.write_ushort(len(sliced))
            stream.write(sliced)
        
        return b"\x03\x05" + stream.buffer + b"\x00\x00"
