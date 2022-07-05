from sc_compression import Decompressor, Compressor
from sc_compression.signatures import Signatures

import os


def decompress(fp):
    decompressor = Decompressor()
    dec = decompressor.decompress(open(fp, 'rb').read())
    open(os.path.splitext(fp)[0] + "_dec.sc", 'wb').write(dec)


def compress(fp):
    compressor = Compressor()
    comp = compressor.compress(open(fp, 'rb').read(), Signatures.SC, 1)
    open(os.path.splitext(fp)[0] + "_cmp.sc", 'wb').write(comp)


if __name__ == "__main__":
    decompress("game-assets/loading_new.sc")
    #compress("game-assets/loading_dec.sc")
