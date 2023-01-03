#include <iostream>
#include <string>

#include "Decompressor.h"
#include "Utils.h"

void printUsage() {
	printf("Usage: [mode] infile outfile\n");
	printf("\n");
	printf("Modes:\n");
	printf("d - Decompress \"infile\" to \"cache or to outfile\"\n");
}

void processDecompressResult(sc::DECOMPRESSOR_ERROR res) {
	switch (res)
	{
	case sc::DECOMPRESSOR_ERROR::OK:
		printf("File succesfully decompressed to: ");
		break;
	case sc::DECOMPRESSOR_ERROR::FILE_READ_ERROR:
		printf("[ERROR] Failed to read file.");
		break;
	case sc::DECOMPRESSOR_ERROR::FILE_WRITE_ERROR:
		printf("[ERROR] Failed to write file.");
		break;
	case sc::DECOMPRESSOR_ERROR::WRONG_FILE_ERROR:
		printf("[ERROR] Wrong file!\n");
		break;
	case sc::DECOMPRESSOR_ERROR::DECOMPRESS_ERROR:
		printf("[ERROR] Decompression error!");
		break;
	default:
		printf("[ERROR] Unknown error!");
		break;
	}
}

int main(int argc, char** argv)
{
	printf("SC Compression - x86 Test Command Line app - Compiled %s %s\n", __DATE__, __TIME__);
	if (argc < 2) {
		printUsage();
	}

	if (argv[1]) {
		std::string mode(argv[1]);
		if (mode == "d") {
			std::string inFilepath(argv[2]);
			std::string outFilepath;
			sc::DECOMPRESSOR_ERROR res = sc::Decompressor::decompress(inFilepath, outFilepath);
			processDecompressResult(res);
			std::cout << outFilepath << std::endl;
		}
		else {
			printf("Unknown mode");
		}
	}
	else {
		printf("Mode no specified.");
	}

	return 0;
}