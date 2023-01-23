#include "SupercellCompression/Compressor.h"

#include <cstdlib>
#include <ctime>

#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/Endian.h"

#include "SupercellCompression/backend/LzmaCompression.h"
#include "SupercellCompression/backend/ZstdCompression.h"
#include "SupercellCompression/backend/LzhamCompression.h"

#include "SupercellCompression/common/ByteStream.hpp"

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
		if (inFile == NULL)
			return CompressorError::FILE_READ_ERROR;

		FILE* outFile = fopen(outFilepath.c_str(), "wb");
		if (inFile == NULL)
			return CompressorError::FILE_WRITE_ERROR;

		FileStream inputStream = FileStream(inFile);
		FileStream outputStream = FileStream(outFile);

		CompressorError res = compress(inputStream, outputStream, signature);

		inputStream.close();
		outputStream.close();

		return res;
	}

	CompressorError Compressor::compress(BinaryStream& inStream, BinaryStream& outStream, CompressionSignature signature)
	{
		CompressedSwfProps header;
		header.id = std::vector<uint8_t>(ID_SIZE);

		srand(static_cast<uint32_t>(time(NULL)));
		for (uint32_t i = 0; ID_SIZE > i; i++)
		{
			header.id[i] = 1 + (rand() % 253);
		}

		header.signature = (uint32_t)signature;

		return compress(inStream, outStream, header);
	}

	CompressorError Compressor::compress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps& header)
	{
		// SC header
		uint32_t scMagic = 0x53430000;
		outStream.writeUInt32BE(scMagic);

		if (!header.metadata.empty())
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

		outStream.writeUInt32BE(static_cast<uint32_t>(header.id.size()));
		outStream.write(header.id.data(), header.id.size());

		CompressorError res = commonCompress(inStream, outStream, static_cast<CompressionSignature>(header.signature));

		if (!header.metadata.empty())
		{
			outStream.write(static_cast<void*>("START"), 5);
			outStream.write(header.metadata.data(), header.metadata.size());
			outStream.writeUInt32BE(static_cast<uint32_t>(header.metadata.size()));
		}

		return res;
	}

	CompressorError Compressor::commonCompress(BinaryStream& inStream, BinaryStream& outStream, CompressionSignature signature)
	{
		CompressionError res;
		switch (signature)
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
			res = CompressionError::OK;
			break;
		}

		return res == CompressionError::OK ? CompressorError::OK : CompressorError::COMPRESS_ERROR;
	}
}