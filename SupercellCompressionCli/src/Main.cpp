#include <fstream>
#include <iostream>
#include <string>
#include <chrono>

#include "Decompressor.h"
#include "Compressor.h"
#include "Utils.h"
#include "Signature.h"

#if defined _WIN32
#define PLATFORM "Windows"
#elif defined __linux
#define PLATFORM "Linux"
#elif defined __macosx
#define PLATFORM "MacOSX"
#else
#define PLATFORM "Unknown"
#endif

std::string getCmdOption(int argc, char* argv[], const std::string& option)
{
	std::string cmd;
	for (int i = 0; i < argc; ++i)
	{
		std::string arg = argv[i];
		if (0 == arg.find(option))
		{
			std::size_t found = arg.find_first_of("=");
			cmd = arg.substr(found + 1);
			return cmd;
		}
	}
	return cmd;
}

bool optionInCmd(int argc, char* argv[], const std::string& option) {
	for (int i = 0; i < argc; ++i)
	{
		std::string arg = argv[i];
		if (0 == arg.find(option))
		{
			return true;
		}
	}
	return false;
}

char* string_to_hex(char* input, uint32_t len) {
	static const char* const lut = "0123456789ABCDEF";
	int k = 0;
	if (len & 1)
		return NULL;

	char* output = new char[(len / 2) + 1];

	for (uint32_t i = 0, j = 0; i < len; i++, j += 2) {
		const unsigned char c = input[i];
		output[j] = lut[c >> 4];
		output[j + 1] = lut[c & 15];
	}

	output += '\0';
	return output;
}

void printUsage() {
	printf("Usage: [mode] InputFilePath OutputFilePath options\n");
	printf("Options:\n");
	printf("m - compression mode: LZMA, LZHAM, ZSTD. Default: LZMA\n");
	printf("c - enable cache: uses a temporary folder for unpacking files.\n");
	printf("Example: c file.sc file_compressed.sc -m=ZSTD\n");
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

void processFileInfo(sc::CompressedSwfProps info) {
	printf("SCSWF compressed asset info:\n");

	printf("Is .sc file : %s\n", info.ok ? "Yes" : "No");
	// printf("id : %s\n", string_to_hex(info.id, info.idSize));
	printf("Has metadata: %s\n", info.metadataSize != 0 ? "Yes" : "No");
	printf("Has hash: %s\n", info.hashSize != 0 ? "Yes" : "No");

	std::string compressionMethod = "NONE";
	switch (info.signature)
	{
	case 1:
		compressionMethod = "LZMA";
		break;
	case 2:
		compressionMethod = "LZHAM";
		break;
	case 3:
		compressionMethod = "ZSTD";
		break;
	default:
		break;
	}

	printf("Compression method: %s\n", compressionMethod.c_str());

	std::cout << std::endl;

}

int main(int argc, char* argv[])
{
	bool enableCache = optionInCmd(argc, argv, "--cache") || optionInCmd(argc, argv, "-c");

	printf("SC Compression - %s Command Line app - Compiled %s %s\n\n", PLATFORM, __DATE__, __TIME__);
	if (argc <= 1) {
		printUsage();
		std::cout << std::endl;
	}

	if (!argv[1]) {
		std::cout << "[ERROR] Mode is not specified." << std::endl;
		return 0;
	}
	std::string mode(argv[1]);

	std::string inFilepath(argv[2] ? argv[2] : "");
	if (inFilepath.empty() || !sc::Utils::fileExist(inFilepath)) {
		std::cout << "[ERROR] Input file does not exist." << std::endl;
		return 0;
	}

	std::string outFilepath(argv[3] ? argv[3] : "");
	if (outFilepath.empty() && !(enableCache && mode == "d")) {
		std::cout << "[ERROR] Output file does not exist." << std::endl;
		return 0;
	}

	using std::chrono::high_resolution_clock;
	using std::chrono::duration_cast;
	using std::chrono::duration;
	using std::chrono::milliseconds;
	using std::chrono::seconds;

	auto startTime = high_resolution_clock::now();

	if (mode == "d") {
		sc::CompressorErrs res;
		if (enableCache) {
			res = sc::Decompressor::decompress(inFilepath, outFilepath);
		}
		else {
			sc::ScFileStream inStream = sc::ScFileStream(fopen(inFilepath.c_str(), "rb"));
			sc::ScFileStream outStream = sc::ScFileStream(fopen(outFilepath.c_str(), "wb"));

			sc::CompressedSwfProps headerInfo = sc::Decompressor::getHeader(inStream);

			processFileInfo(headerInfo);

			res = sc::Decompressor::decompress(inStream, outStream, headerInfo);
		}
		
		processCompressorErrs(res);
		if (res == sc::CompressorErrs::OK) {
			std::cout << outFilepath << std::endl;
		}
	}
	else if (mode == "c") {
		sc::CompressionSignatures signature = sc::CompressionSignatures::LZMA_COMPRESSION;

		std::string signatureArg = getCmdOption(argc, argv, "-m=");

		if (signatureArg == "ZSTD") {
			signature = sc::CompressionSignatures::ZSTD_COMRESSION;
		}
		else if (signatureArg == "LZHAM") {
			signature = sc::CompressionSignatures::LZHAM_COMPRESSION;
		}

		sc::CompressorErrs res = sc::Compressor::compress(inFilepath, outFilepath, signature);

		processCompressorErrs(res);
		if (res == sc::CompressorErrs::OK) {
			std::cout << outFilepath << std::endl;
		}
	}
	else {
		printf("[ERROR] Unknown mode.");
		return 0;
	}

	auto endTime = high_resolution_clock::now();
	std::cout << "[INFO] Operation took: ";

	milliseconds msTime = duration_cast<milliseconds>(endTime - startTime);
	if (msTime.count() < 1000) {
		std::cout << msTime.count() << " miliseconds";
	}
	else {
		auto secondTime = duration_cast<seconds>(endTime - startTime);
		std::cout << secondTime.count() << " seconds";
	}

	return 0;
}