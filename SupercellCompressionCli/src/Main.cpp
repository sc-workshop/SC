#include <fstream>
#include <iostream>
#include <string>
#include <chrono>

#include "Decompressor.h"
#include "Compressor.h"
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

void processCompressorErrs(sc::CompressorErrs res) {
	switch (res)
	{
	case sc::CompressorErrs::OK:
		std::cout << "[INFO] File successfully processed into:  ";
		break;
	case sc::CompressorErrs::FILE_READ_ERROR:
		std::cout << "[ERROR] Failed to read file." << std::endl;
		break;
	case sc::CompressorErrs::FILE_WRITE_ERROR:
		std::cout << "[ERROR] Failed to write file." << std::endl;
		break;
	case sc::CompressorErrs::WRONG_FILE_ERROR:
		std::cout << "[ERROR] Wrong file!" << std::endl;
		break;
	case sc::CompressorErrs::DECOMPRESS_ERROR:
		std::cout << "[ERROR] Decompression error!" << std::endl;
		break;
	default:
		std::cout << "[ERROR] Unknown error!" << std::endl;
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
		std::cout << "[INFO] Mode is not specified. Exit..." << std::endl;
		exit(0);
	}
	std::string mode(argv[1]);

	if (!argv[2]) {
		std::cout << "[ERROR] Input file path is not specified." << std::endl;
		exit(0);
	}

	std::string inFilepath(argv[2]);

	if (!sc::Utils::fileExist(inFilepath)) {
		std::cout << "[ERROR] Input file does not exist." << std::endl;
		exit(0);
	}

	std::string outFilepath;
	if (argv[3]) {
		outFilepath = argv[3];
	}

	using std::chrono::high_resolution_clock;
	using std::chrono::duration_cast;
	using std::chrono::duration;
	using std::chrono::milliseconds;
	using std::chrono::seconds;

	auto startTime = high_resolution_clock::now();

	if (mode == "d") {
		
		sc::CompressorErrs res;
		if (outFilepath.empty()) {
			res = sc::Decompressor::decompress(inFilepath, outFilepath);
		}
		else {

			sc::ScFileStream inStream = sc::ScFileStream(fopen(inFilepath.c_str(), "rb"));
			sc::ScFileStream outStream = sc::ScFileStream(fopen(outFilepath.c_str(), "wb"));

			res = sc::Decompressor::decompress(inStream, outStream);
		}

		processCompressorErrs(res);
		if (res == sc::CompressorErrs::OK) {
			std::cout << outFilepath << std::endl;
		}
	}
	else if (mode == "c") {
		;
		if (outFilepath.empty()) {
			std::cout << "[ERROR] Output file path is not specified." << std::endl;
		}

		sc::CompressPressets presset = sc::CompressPressets::NORMAL;

		sc::CompressorErrs res = sc::Compressor::compress(inFilepath, outFilepath, presset);

		processCompressorErrs(res);
		if (res == sc::CompressorErrs::OK) {
			std::cout << outFilepath << std::endl;
		}
	}
	else {
		printf("[ERROR] Unknown mode.");
		exit(0);
	}

	auto endTime = high_resolution_clock::now();
	std::cout << "[INFO] Operation took: ";

	auto msTime = duration_cast<milliseconds>(endTime - startTime);
	if (msTime.count() < 1000) {
		std::cout << msTime.count() << " miliseconds";
	}
	else {
		auto secondTime = duration_cast<seconds>(endTime - startTime);
		std::cout << secondTime.count() << " seconds";
	}

	

	return 0;
}