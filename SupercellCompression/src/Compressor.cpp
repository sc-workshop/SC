#include <stdlib.h>
#include <time.h>

#include "Utils.h"
#include "Signature.h"
#include "Endian.h"
#include "Compressor.h"

#include "LzmaCompression.h"
#include "ZstdCompression.h"
#include "LzhamCompression.h"
#include "ByteStream.hpp"

constexpr uint32_t ID_SIZE = 16;

namespace sc
{
	CompressorError Compressor::compress(const std::string& inputFilepath, std::string outFilepath, CompressionSignature signature)
	{
		if (!Utils::fileExist(inputFilepath))
		{
			return CompressorError::WRONG_FILE_ERROR;
		}

		FILE* inFile = fopen(inputFilepath.c_str(), "rb");
		FILE* outFile = fopen(outFilepath.c_str(), "wb");

		ScFileStream inputStream = ScFileStream(inFile);
		ScFileStream outputStream = ScFileStream(outFile);

		CompressedSwfProps header;
		header.idSize = ID_SIZE;
		header.id = new char[header.idSize]();

		srand(static_cast<uint32_t>(time(NULL)));
		for (uint32_t i = 0; header.idSize > i; i++)
		{
			header.id[i] = rand() % 253 + (-126);
		}

		header.signature = (uint32_t)signature;

		CompressorError res = compress(inputStream, outputStream, header);

		inputStream.close();
		outputStream.close();

		return res;
	}

	CompressorError Compressor::compress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps& header)
	{
		// SC header
		uint32_t scMagic = 0x53430000;
		outStream.writeUInt32BE(scMagic);

		if (header.metadataSize > 0)
		{
			outStream.writeUInt16BE(4);
			outStream.writeUInt32BE(header.signature);
		}
		else
		{
			if (header.signature == (uint32_t)CompressionSignature::LZMA ||
				header.signature == (uint32_t)CompressionSignature::LZHAM)
			{
				outStream.writeUInt16BE(1);
			}
			else if (header.signature == (uint32_t)CompressionSignature::ZSTD)
			{
				outStream.writeUInt16BE(3);
			}
			else
			{
				outStream.writeUInt16BE(2);
			}
		}

		outStream.writeUInt32BE(header.idSize);
		outStream.write(header.id, header.idSize);

		CompressorError res = commonCompress(inStream, outStream, header.signature);

		if (header.metadataSize > 0)
		{
			outStream.write("START", 5);
			outStream.write(&header.metadata, header.metadataSize);
			outStream.writeUInt32(header.metadataSize);
		}

		return res;
	}

	CompressorError Compressor::commonCompress(IBinaryStream& inStream, IBinaryStream& outStream, uint32_t signatureIndex)
	{
		CompressionError res = CompressionError::OK;
		switch ((CompressionSignature)signatureIndex)
		{
		case CompressionSignature::LZMA:
			res = LZMA::compress(inStream, outStream);
			break;

		case CompressionSignature::LZHAM:
			res = LZHAM::compress(inStream, outStream);
			break;

		case CompressionSignature::ZSTD:
			res = ZSTD::compress(inStream, outStream);
			break;

		default:
			size_t size = inStream.size() - inStream.tell();
			void* dataBuffer = malloc(size);
			inStream.read(dataBuffer, size);
			outStream.write(dataBuffer, size);
			free(dataBuffer);
			break;
		}

		return res == CompressionError::OK ? CompressorError::OK : CompressorError::COMPRESS_ERROR;
	}
}