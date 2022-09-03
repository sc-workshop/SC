import os

import time
import argparse

from sc_compression.signatures import Signatures
from sc_compression import Decompressor, Compressor

from lib.console import Console, Time

def main():
    parser = argparse.ArgumentParser(description="SC tool by SCW Make - github.com/scwmake/SC")

    parser.add_argument("-d", "--decompile", help="Convert *.sc file to *.fla", type=str)
    parser.add_argument("-c", "--compile", help="Convert *.fla to *.sc file", type=str)

    parser.add_argument("-dx", "--decompress", help="Decompress *.sc files with Supercell compression", type=str)
    parser.add_argument("-cx", "--compress", help="Compress *.sc files with Supercell compression (LZMA | SC | version 1)", type=str)

    parser.add_argument("-dj", "--decompile-json", help="Convert *.sc file to *.json file", type=str)
    parser.add_argument("-cj", "--compile-json", help="Convert *.json file to *.sc file", type=str)

    args = parser.parse_args()

    start_time = time.time()

    if args.decompile:
        from lib import sc_to_fla
        sc_to_fla(args.decompile)

    elif args.compile:
        from lib import fla_to_sc
        fla_to_sc(args.compile)

    elif args.decompress:
        file = args.decompress

        decompressor = Decompressor()
        decompressed = decompressor.decompress(open(file, 'rb').read().split(b"START")[0])

        open(file + ".dec", 'wb').write(decompressed)

    elif args.compress:
        file = args.compress

        compressor = Compressor()
        compressed = compressor.compress(open(file, 'rb').read(), Signatures.SC, 1)

        open(file + ".cmp", 'wb').write(compressed)


    elif args.decompile_json:
        from lib.json_import import sc_to_json
        sc_to_json(args.decompile_json)

    elif args.compile_json:
        from lib.json_export import json_to_sc
        json_to_sc(args.compile_json)

    else:
        Console.title("SC tool by SCW Make - github.com/scwmake/SC")
        print("-d, --decompile : Convert *.sc file to *.fla")
        print("-c, --compile : Convert *.fla to *.sc file")
        print("-dx, --decompress : Decompress *.sc files with Supercell compression")
        print("-cx, --compress : Compress *.sc files with Supercell compression (LZMA | SC | version 1)")
        print("-dj, --decompile-json : Convert *.sc file to *.json file")
        print("-cj, --compile-json : Convert *.json file to *.sc file")
        exit(0)

    result_time = time.time() - start_time

    print(f"Done in {Time(result_time)} seconds!")


if __name__ == "__main__":
    main()
