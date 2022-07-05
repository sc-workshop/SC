from zlib import decompress, compress

from struct import unpack, pack

import numpy as np


class Bitmap:
    @staticmethod
    def load(filepath: str):
        file = open(filepath, 'rb')

        magic, = unpack("<h", file.read(2))
        if magic != 1283:
            raise Exception(f"Bad \".dat\" file: {filepath}")

        file.read(2)  # row data length

        width, = unpack("<H", file.read(2))
        height, = unpack("<H", file.read(2))

        file.read(4)  # unknown
        file.read(4)  # width in twips

        file.read(4)  # unknown
        file.read(4)  # height in twips

        flags, = unpack("B", file.read(1))
        compression, = unpack("?", file.read(1))

        header = bytes()
        if compression:
            header_length, = unpack("<H", file.read(2))
            header = file.read(header_length)

        alpha = (flags & 1) != 0

        image_binary_data = bytes()
        while True:
            data_block_size, = unpack("<H", file.read(2))

            if data_block_size == 0:
                break

            image_binary_data += file.read(data_block_size)

        file.close()

        mode = 4 if alpha else 3

        if compression:
            image_binary_data = decompress(header + image_binary_data)

        img = np.fromstring(image_binary_data, np.uint8).reshape(height, width, mode)[:, :, ::-1]
        return img

    @staticmethod
    def save(filepath: str, image, compression: bool = True):
        height, width, channels = image.shape

        alpha = channels == 4

        image_binary_data = []
        for x in range(height):
            for y in range(width):
                pixel = image[x, y]
                if alpha:
                    r, g, b, a = pixel
                    image_binary_data.append(r << 24 | g << 16 | b << 8 | a)
                else:
                    r, g, b = pixel
                    image_binary_data.append(r << 24 | g << 16 | b << 8)

        image_binary_data = np.array(image_binary_data, dtype="<I").tobytes()

        if compression:
            image_binary_data = compress(image_binary_data)

        file = open(filepath, 'wb')

        file.write(pack("<h", 1283))  # magic

        file.write(pack("<H", (width + height) * 2))  # row data length

        file.write(pack("<H", width))
        file.write(pack("<H", height))

        file.write(bytes(4))  # unknown
        file.write(pack("<I", width * 20))  # width in twips

        file.write(bytes(4))  # unknown
        file.write(pack("<I", height * 20))  # height in twips

        file.write(pack("B", int(alpha)))
        file.write(pack("?", compression))

        if compression:
            header = image_binary_data[:2]

            file.write(pack("<H", len(header)))
            file.write(header)

            image_binary_data = image_binary_data[2:]

        if len(image_binary_data) < 2048:
            file.write(pack("<H", len(image_binary_data)))
            file.write(image_binary_data)
        else:
            blocks = [image_binary_data[i:i + 2048] for i in range(0, len(image_binary_data), 2048)]
            for block in blocks:
                file.write(pack("<H", len(block)))
                file.write(block)

        file.write(bytes(2))

        file.close()
