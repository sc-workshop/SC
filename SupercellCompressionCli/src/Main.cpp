#include <iostream>
#include <string>

#include "Decompressor.h"
#include "Utils.h"

#if defined _WIN32
#define PLATFORM "Windows"
#elif defined __linux
#define PLATFORM "Linux"
#elif defined __macosx
#define PLATFORM "MacOSX"
#else
#define PLATFORM "Unknown"
#endif

void printUsage() {
	printf("Usage: [mode] infile outfile\n");
	printf("\n");
	printf("Modes:\n");
	printf("d - Decompress \"infile\" to \"cache\"\n");
}

void processDecompressResult(sc::DecompressorErrs res) {
	switch (res)
	{
	case sc::DecompressorErrs::OK:
		printf("File succesfully decompressed to: ");
		break;
	case sc::DecompressorErrs::FILE_READ_ERROR:
		printf("[ERROR] Failed to read file.");
		break;
	case sc::DecompressorErrs::FILE_WRITE_ERROR:
		printf("[ERROR] Failed to write file.");
		break;
	case sc::DecompressorErrs::WRONG_FILE_ERROR:
		printf("[ERROR] Wrong file!");
		break;
	case sc::DecompressorErrs::DECOMPRESS_ERROR:
		printf("[ERROR] Decompression error!");
		break;
	default:
		printf("[ERROR] Unknown error!");
		break;
	}
}

int main(int argc, char** argv)
{
	printf("SC Compression - %s Command Line app - Compiled %s %s\n", PLATFORM, __DATE__, __TIME__);
	if (argc < 2) {
		printUsage();
		std::cout << std::endl;
	}

	std::string mode(argv[1]);
	std::string inFilepath(argv[2]);

	if (mode.empty()) {
		printf("[INFO] Mode is not specified. Exit...");
	}

	if (inFilepath.empty()) {
		printf("[ERROR] Input file path is not specified.");
	}

	if (mode == "d") {
		std::string outFilepath;
		sc::DecompressorErrs res = sc::Decompressor::decompress(inFilepath, outFilepath);

		processDecompressResult(res);
		if (res == sc::DecompressorErrs::OK) {
			std::cout << outFilepath << std::endl;
		}
	}
	else {
		printf("[ERROR] Unknown mode.");
	}

	return 0;
}