import argparse
import time

from sc_compression import Decompressor, Compressor
from sc_compression.signatures import Signatures

from lib.time import time_to_string


def main():
    parser = argparse.ArgumentParser(description="SC tool by SCW Make - https://github.com/scwmake/SC")

    parser.add_argument("-d", "--decompile", help="Convert *.sc file to *.fla", type=str)
    parser.add_argument("-dx", "--decompress", help="Decompress *.sc files with Supercell compression", type=str)
    parser.add_argument("-cx", "--compress",
                        help="Compress *.sc files with Supercell compression (LZMA | SC | version 1)", type=str)

    args = parser.parse_args()

    start_time = time.time()

    if args.decompile:
        from lib import sc_to_fla
        sc_to_fla(args.decompile)
    elif args.decompress:
        file_path = args.decompress

        with open(file_path, 'rb') as file:
            decompressor = Decompressor()
            decompressed = decompressor.decompress(file.read().split(b"START")[0])

        with open(file_path + ".dec", 'wb') as decompressed_file:
            decompressed_file.write(decompressed)
    elif args.compress:
        file_path = args.compress

        with open(file_path, 'rb') as file:
            compressor = Compressor()
            compressed = compressor.compress(file.read(), Signatures.SC, 1)

        with open(file_path + ".cmp", 'wb') as compressed_file:
            compressed_file.write(compressed)
    else:
        parser.print_help()
        exit()

    print(f"Done in {time_to_string(time.time() - start_time)} seconds!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
