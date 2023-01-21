#include <fstream>
#include <iostream>
#include <string>
#include <chrono>

#include <SupercellCompression.h>

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

void printUsage() {
	printf("Usage: [mode] InputFilePath OutputFilePath options\n");
	printf("Modes:\n");
	printf("c - compress file.\n");
	printf("d - decompress file.\n");
	printf("Options:\n");
	printf("-m - compression mode: LZMA, LZHAM, ZSTD. Default: LZMA\n");
	printf("--cache - enable cache: uses a temporary folder for unpacking files.\n");
	printf("Example: c file.sc file_compressed.sc -m=ZSTD\n");
}

void processCompressorErrs(sc::CompressorError res) {
	switch (res)
	{
	case sc::CompressorError::OK:
		std::cout << "[INFO] File successfully processed into:  ";
		break;
	case sc::CompressorError::FILE_READ_ERROR:
		std::cout << "[ERROR] Failed to read file." << std::endl;
		break;
	case sc::CompressorError::FILE_WRITE_ERROR:
		std::cout << "[ERROR] Failed to write file." << std::endl;
		break;
	case sc::CompressorError::WRONG_FILE_ERROR:
		std::cout << "[ERROR] Wrong file!" << std::endl;
		break;
	case sc::CompressorError::DECOMPRESS_ERROR:
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

	static const char hexDigits[] = "0123456789ABCDEF";
	std::cout << "Id: ";
	for (uint8_t c : info.id)
	{
		std::cout << hexDigits[c >> 4] << hexDigits[c & 15] << " ";
	}
	std::cout << std::endl;

	printf("Has metadata: %s\n", info.metadata.empty() ? "Yes" : "No");
	printf("Has hash: %s\n", info.hash.empty() ? "Yes" : "No");

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
	bool enableCache = optionInCmd(argc, argv, "--cache");
	bool memoryStream = optionInCmd(argc, argv, "--memory-stream");

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

	std::string outFilepath(argv[3] && !enableCache ? argv[3] : "");
	if (outFilepath.empty() && !(enableCache && mode == "d")) {
		std::cout << "[ERROR] Output file does not exist." << std::endl;
		return 0;
	}

	using std::chrono::high_resolution_clock;
	using std::chrono::duration_cast;
	using std::chrono::duration;
	using std::chrono::milliseconds;
	using std::chrono::seconds;

	std::chrono::time_point startTime = high_resolution_clock::now();

	if (mode == "d") {
		sc::CompressorError res;

		if (enableCache) {
			res = sc::Decompressor::decompress(inFilepath, outFilepath);
		}
		else if (memoryStream) {
			FILE* inFile;
			FILE* outFile;

			fopen_s(&inFile, inFilepath.c_str(), "rb");
			fopen_s(&outFile, outFilepath.c_str(), "wb");

			if (!inFile || !outFile) {
				std::cout << "[ERROR] Failed to open files!" << std::endl;
				return 0;
			}

			uint32_t inBufferSize = sc::Utils::fileSize(inFile);
			std::vector<uint8_t> inBuffer(inBufferSize);
			fread(inBuffer.data(), 1, inBufferSize, inFile);
			sc::BufferStream inStream(&inBuffer);

			std::vector<uint8_t> outBuffer;
			sc::BufferStream outStream(&outBuffer);

			res = sc::Decompressor::decompress(inStream, outStream);

			fwrite(outBuffer.data(), 1, outBuffer.size(), outFile);

			inStream.close();
			outStream.close();
		}
		else {
			FILE* inFile;
			FILE* outFile;

			fopen_s(&inFile, inFilepath.c_str(), "rb");
			fopen_s(&outFile, outFilepath.c_str(), "wb");

			sc::FileStream inStream = sc::FileStream(inFile);
			sc::FileStream outStream = sc::FileStream(outFile);

			sc::CompressedSwfProps headerInfo = sc::Decompressor::getHeader(inStream);

			processFileInfo(headerInfo);

			res = sc::Decompressor::decompress(inStream, outStream, headerInfo);
		}

		processCompressorErrs(res);
		if (res == sc::CompressorError::OK) {
			std::cout << outFilepath << std::endl;
		}
	}
	else if (mode == "c") {
		sc::CompressionSignature signature = sc::CompressionSignature::LZMA;

		std::string signatureArg = getCmdOption(argc, argv, "-m=");

		if (signatureArg == "ZSTD") {
			signature = sc::CompressionSignature::ZSTD;
		}
		else if (signatureArg == "LZHAM") {
			signature = sc::CompressionSignature::LZHAM;
		}

		sc::CompressorError res = sc::Compressor::compress(inFilepath, outFilepath, signature);

		processCompressorErrs(res);
		if (res == sc::CompressorError::OK) {
			std::cout << outFilepath << std::endl;
		}
	}
	else {
		printf("[ERROR] Unknown mode.");
		return 0;
	}

	std::chrono::time_point endTime = high_resolution_clock::now();
	std::cout << "[INFO] Operation took: ";

	milliseconds msTime = duration_cast<milliseconds>(endTime - startTime);
	if (msTime.count() < 1000) {
		std::cout << msTime.count() << " miliseconds.";
	}
	else {
		seconds secTime = duration_cast<seconds>(msTime);
		std::cout << secTime.count() << " seconds." << std::endl;
	}

	return 0;
}