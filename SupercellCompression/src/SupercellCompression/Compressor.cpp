#include "SupercellCompression/Compressor.h"

#include <cstdlib>
#include <ctime>

#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/Endian.h"

#include "SupercellCompression/backend/LzmaCompression.h"
#include "SupercellCompression/backend/ZstdCompression.h"
#include "SupercellCompression/backend/LzhamCompression.h"

#include "SupercellCompression/common/ByteStream.hpp"
#include "SupercellCompression/common/md5.h"

constexpr uint32_t ID_SIZE = 16;

namespace sc
{
	CompressorError Compressor::compress(const std::string& inputFilepath, const std::string& outFilepath, CompressionSignature signature)
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

		Chocobo1::MD5 md5;

		uint32_t buffSize = 0x7D000; // 512 kb 

		void* buff = malloc(buffSize);

		while (const size_t readSize = inStream.read(buff, buffSize)) {
			md5.addData(buff, readSize);
		}

		md5.finalize();

		free(buff);

		header.id = md5.toVector();
		header.signature = signature;

		return compress(inStream, outStream, header);
	}

	CompressorError Compressor::compress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps& header)
	{
		const uint16_t scMagic = 0x5343;

		outStream.writeUInt16BE(scMagic);
		if (!header.metadata.empty())
		{
			outStream.writeUInt32BE(4);
			outStream.writeUInt32BE((uint32_t)header.signature);
		}
		else
		{
			if (header.signature == CompressionSignature::LZMA ||
				header.signature == CompressionSignature::LZHAM)
			{
				outStream.writeUInt32BE(1);
			}
			else if (header.signature == CompressionSignature::ZSTD)
			{
				outStream.writeUInt32BE(3);
			}
			else
			{
				outStream.writeUInt32BE(2);
			}
		}

		outStream.writeUInt32BE(static_cast<uint32_t>(header.id.size()));
		outStream.write(header.id.data(), header.id.size());

		CompressorError res = commonCompress(inStream, outStream, header.signature);

		if (!header.metadata.empty())
		{
			char* start = "START";
			outStream.write(&start, 5);
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
			std::vector<uint8_t> dataBuffer(inStream.size());
			inStream.set(0);
			inStream.read(dataBuffer.data(), dataBuffer.size());
			outStream.write(dataBuffer.data(), dataBuffer.size());
			res = CompressionError::OK;
			break;
		}

		return res == CompressionError::OK ? CompressorError::OK : CompressorError::COMPRESS_ERROR;
	}
}