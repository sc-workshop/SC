#include "Utils.h"
#include "Signature.h"
#include "Endian.h"
#include "Compressor.h"

#include "LzmaCompression.h"

#include <stdlib.h>

constexpr uint32_t ID_SIZE = 16;

namespace sc
{
	CompressorErrs Compressor::compress(std::string inputFilepath, std::string outFilepath, CompressPressets presset) {
		if (!Utils::fileExist(inputFilepath)) {
			return CompressorErrs::WRONG_FILE_ERROR;
		}

		FILE* inFile = fopen(inputFilepath.c_str(), "rb");
		FILE* outFile = fopen(outFilepath.c_str(),  "wb");

		ScFileStream inputStream = ScFileStream(inFile);
		ScFileStream outputStream = ScFileStream(outFile);

		CompressedSwfProps header;
		header.idSize = ID_SIZE;
		header.id = new char[header.idSize]();
		for (uint32_t i = 0; header.idSize > i; i++) {
			header.id[i] = rand() % 254 + 1;
		}

		if (presset == CompressPressets::FAST) {
			header.signature = CompressionSignatures::ZSTD_COMRESSION;
		}
		else if (presset == CompressPressets::NORMAL) {
			header.signature = CompressionSignatures::LZMA_COMPRESSION;
		}

		CompressorErrs res = compress(inputStream, outputStream, header);

		inputStream.close();
		outputStream.close();

		return res;
	}

	CompressorErrs Compressor::compress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps& header) {
		// SC header
		uint32_t scMagic = 0x53430000;
		outStream.writeUInt32BE(scMagic);

		uint16_t version = 1;
		if (header.metadataSize > 0) {
			version = 4;
			outStream.writeUInt16BE(version);
			outStream.writeUInt32BE(header.signature);
		}
		else {
			outStream.writeUInt16BE(version);
		}

		outStream.writeUInt32BE(header.idSize);
		outStream.write(header.id, header.idSize);

		CompressionErrs res;
		switch (header.signature)
		{
		case CompressionSignatures::LZMA_COMPRESSION:
			res = LZMA::compress(inStream, outStream);
			break;
		default:
			res = CompressionErrs::OK;
			break;
		}

		if (version == 4) {
			outStream.write("START", 5);
			outStream.write(&header.metadata, header.metadataSize);
			outStream.writeUInt32(header.metadataSize);
		}
		
		return res == CompressionErrs::OK ? CompressorErrs::OK : CompressorErrs::COMPRESS_ERROR;
	}
}