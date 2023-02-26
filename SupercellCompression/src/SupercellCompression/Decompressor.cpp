#include "SupercellCompression/Decompressor.h"

#include <iostream>

#include "SupercellCompression/cache/Cache.h"
#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/Endian.h"

#include "SupercellCompression/backend/LzmaCompression.h"
#include "SupercellCompression/backend/LzhamCompression.h"
#include "SupercellCompression/backend/ZstdCompression.h"

#include "SupercellCompression/common/ByteStream.hpp"

namespace sc
{
	CompressorError Decompressor::decompress(const std::string& filepath, std::string& outFilepath, std::vector<uint8_t>* metadata)
	{
		/* Some check */
		if (!Utils::endsWith(filepath, ".sc")) {
			return CompressorError::WRONG_FILE_ERROR;
		}

		if (!Utils::fileExist(filepath))
			return CompressorError::FILE_READ_ERROR;

		/* Input file opening */

		FILE* inputFile = fopen(filepath.c_str(), "rb");
		if (inputFile == NULL)
			return CompressorError::FILE_READ_ERROR;

		FileStream inputStream = FileStream(inputFile);
		uint32_t fileSize = inputStream.size();

		/* Caching things */

		outFilepath = SwfCache::getTempPath(filepath);

		/* Header parsing */
		CompressedSwfProps header = getHeader(inputStream);
		if (metadata != nullptr) {
			metadata = &header.metadata;
		}

		bool fileInCache = SwfCache::exist(filepath, header.id, fileSize);
		if (fileInCache)
		{
			return CompressorError::OK;
		}

		FILE* outFile = fopen(outFilepath.c_str(), "wb");
		if (outFile == NULL)
			return CompressorError::FILE_WRITE_ERROR;

		FileStream outputStream = FileStream(outFile);

		CompressorError res = decompress(inputStream, outputStream, &header);

		inputStream.close();
		outputStream.close();

		if (res == CompressorError::OK && !fileInCache)
		{
#ifndef DISABLE_CACHE
			SwfCache::addData(filepath, header, fileSize);
#endif
		}

		return res;
	}

	CompressorError Decompressor::decompress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps* header)
	{
		*header = getHeader(inStream);

		return decompress(inStream, outStream, *header);
	}

	CompressorError Decompressor::commonDecompress(BinaryStream& inStream, BinaryStream& outStream, CompressionSignature signature) {
		CompressionError res;

		switch (signature)
		{
		case CompressionSignature::LZMA:
			res = LZMA::decompress(inStream, outStream);
			break;

		case CompressionSignature::LZHAM:
			res = LZHAM::decompress(inStream, outStream);
			break;

		case CompressionSignature::ZSTD:
			res = ZSTD::decompress(inStream, outStream);
			break;

		default:
			std::vector<uint8_t> dataBuffer(inStream.size());
			inStream.set(0);
			inStream.read(dataBuffer.data(), dataBuffer.size());
			outStream.write(dataBuffer.data(), dataBuffer.size());

			res = CompressionError::OK;
			break;
		}

		return res == CompressionError::OK ? CompressorError::OK : CompressorError::DECOMPRESS_ERROR;
	}

	CompressorError Decompressor::commonDecompress(BinaryStream& inStream, BinaryStream& outStream) {
		inStream.set(0);
		uint32_t magic;
		inStream.read(&magic, sizeof(magic));
		inStream.set(0);

		if (magic == 0x3A676953) {
			inStream.skip(64);
			inStream.read(&magic, sizeof(magic));
		}

		CompressionSignature signature = getSignature(magic);

		return commonDecompress(inStream, outStream, signature);
	}

	CompressedSwfProps Decompressor::getHeader(BinaryStream& inputSteam) {
		CompressedSwfProps header;

		uint16_t magic = inputSteam.readUInt16BE();
		if (magic != 0x5343) { // Just a little trick to handle decompressed file
			header.signature = CompressionSignature::NONE;
			return header;
		}

		// Version of .sc file
		uint32_t version = inputSteam.readUInt32BE();

	VERSION_CHECK:
		switch (version)
		{
		case 4:
		{
			version = inputSteam.readUInt32BE();

			// Metadata processing
			size_t compressedDataStartPosition = inputSteam.tell();
			inputSteam.set(static_cast<uint32_t>(inputSteam.size()) - 4);
			uint32_t metadataSize = inputSteam.readUInt32BE();

			header.metadata = std::vector<uint8_t>(metadataSize);
			inputSteam.set(static_cast<uint32_t>(inputSteam.size() - (metadataSize + 4)));
			inputSteam.read(header.metadata.data(), metadataSize);

			inputSteam.set(static_cast<uint32_t>(compressedDataStartPosition));
			goto VERSION_CHECK;
		}
		case 3:
			header.signature = CompressionSignature::ZSTD;
			break;
		case 1:
			break;
		default:
			return header;
		}

		uint32_t idSize = inputSteam.readUInt32BE();
		header.id = std::vector<uint8_t>(idSize);
		inputSteam.read(header.id.data(), idSize);

		if (version == 1)
		{
			uint32_t compressMagic = inputSteam.readUInt32();

			// Sig
			if (compressMagic == 0x3A676953)
			{
				header.sign = std::vector<uint8_t>(64);
				inputSteam.read(header.sign.data(), 64);
				compressMagic = inputSteam.readUInt32();
			}

			// SCLZ
			if (compressMagic == 0x5A4C4353)
			{
				header.signature = CompressionSignature::LZHAM;
			}

			// LZMA
			else
			{
				header.signature = CompressionSignature::LZMA;
			}

			inputSteam.set(inputSteam.tell() - 4);
		}

		return header;
	}

	CompressorError Decompressor::decompress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps header) {
		if (header.metadata.size() > 0) {
			inStream.setEof(static_cast<uint32_t>(header.metadata.size() + 9));
		}

		CompressorError res = commonDecompress(inStream, outStream, header.signature);
		inStream.setEof(0);

		return res;
	}
}