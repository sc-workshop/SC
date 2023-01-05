#include <fstream>
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

	if (!argv[1]) {
		printf("[INFO] Mode is not specified. Exit...");
		exit(0);
	}
	std::string mode(argv[1]);

	if (!argv[2]) {
		printf("[ERROR] Input file path is not specified.");
		exit(0);
	}

	std::string inFilepath(argv[2]);

	if (!sc::Utils::fileExist(inFilepath)) {
		printf("[ERROR] Input file does not exist.");
		exit(0);
	}

	std::string outFilepath;
	if (argv[3]) {
		outFilepath = argv[3];
	}

	if (mode == "d") {
		
		sc::DecompressorErrs res;
		if (outFilepath.empty()) {
			res = sc::Decompressor::decompress(inFilepath, outFilepath);
		}
		else {

			sc::ScFileStream inStream = sc::ScFileStream(fopen(inFilepath.c_str(), "rb"));
			sc::ScFileStream outStream = sc::ScFileStream(fopen(outFilepath.c_str(), "wb"));

			res = sc::Decompressor::decompress(inStream, outStream);
		}

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