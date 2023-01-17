#include <iostream>

#include "Decompressor.h"
#include "Signature.h"
#include "Cache.h"
#include "Utils.h"
#include "Endian.h"

#include "LzmaCompression.h"
#include "LzhamCompression.h"
#include "ZstdCompression.h"
#include "ByteStream.hpp"

namespace sc
{
	// Decompress SC file
	CompressorError Decompressor::decompress(std::string filepath, std::string& outFilepath)
	{
		if (!Utils::endsWith(filepath, ".sc")) {
			return CompressorError::WRONG_FILE_ERROR;
		}

		if (!Utils::fileExist(filepath))
			return CompressorError::FILE_READ_ERROR;

		FILE* inFile;
		fopen_s(&inFile, filepath.c_str(), "rb");
		if (!inFile)
			return CompressorError::FILE_READ_ERROR;

		ScFileStream inputSteam = ScFileStream(inFile);
		uint32_t fileSize = Utils::fileSize(inFile);

		CompressedSwfProps header = getHeader(inputSteam);
		if (!header.ok)
		{
			return CompressorError::WRONG_FILE_ERROR;
		}

		outFilepath = SwfCache::getTempPath(filepath);
		bool fileInCache = SwfCache::exist(filepath, header.id, fileSize);
		if (fileInCache)
		{
			return CompressorError::OK;
		}

		FILE* outFile;
		fopen_s(&outFile, outFilepath.c_str(), "wb");
		if (!outFile)
			return CompressorError::FILE_WRITE_ERROR;

		ScFileStream outputStream = ScFileStream(outFile);

		CompressorError res = decompress(inputSteam, outputStream, header);

		inputSteam.close();
		outputStream.close();

		if (res == CompressorError::OK && !fileInCache)
		{
#ifndef DISABLE_CACHE
			SwfCache::addData(filepath, header, fileSize);
#endif
		}

		return res;
	}

	CompressorError Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream)
	{
		CompressedSwfProps header = getHeader(inStream);
		if (!header.ok)
			return CompressorError::WRONG_FILE_ERROR;

		return decompress(inStream, outStream, header);
	}

	CompressorError Decompressor::commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressionSignature signature) {
		CompressionError res;

		switch (signature)
		{
		case CompressionSignature::LZMA:
			res = LZMA::decompress(inStream, outStream);
			break;

		case CompressionSignature::ZSTD:
			res = ZSTD::decompress(inStream, outStream);
			break;

		case CompressionSignature::LZHAM:
			res = LZHAM::decompress(inStream, outStream);
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

		return res == CompressionError::OK ? CompressorError::OK : CompressorError::DECOMPRESS_ERROR;
	}

	CompressorError Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps header) {
		inStream.setEof(static_cast<__int64>(header.metadataSize) + header.metadataSize != 0 ? 9 : 0);

		CompressorError res = commonDecompress(inStream, outStream, static_cast<CompressionSignature>(header.signature));

		inStream.setEof(0);

		return res;
	}

	CompressorError Decompressor::commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		inStream.set(0);
		uint32_t magic;
		inStream.read(&magic, sizeof(magic));
		inStream.set(0);

		CompressionSignature signature = getSignature(magic);

		return commonDecompress(inStream, outStream, signature);
	}

	CompressedSwfProps Decompressor::getHeader(IBinaryStream& inputSteam) {
		// .sc file header
		uint32_t magic = inputSteam.readUInt32BE();

		// Version of .sc file
		uint16_t version = inputSteam.readUInt16BE();

		CompressionSignature signature = CompressionSignature::NONE;
		char* metadata{};
		uint32_t metadataSize = 0;
		char* hash{};
		uint32_t hashSize = 0;

		if (version == 3)
		{
			signature = CompressionSignature::ZSTD;
		}
		else if (version == 4)
		{
			signature = static_cast<CompressionSignature>(inputSteam.readUInt32BE());

			// Metadata processing
			size_t origPos = inputSteam.tell();
			inputSteam.set(static_cast<uint32_t>(inputSteam.size()) - 4);
			metadataSize = inputSteam.readUInt32BE();

			metadata = new char[metadataSize]();
			inputSteam.set(static_cast<uint32_t>(inputSteam.size() - (metadataSize + 4)));
			inputSteam.read(metadata, metadataSize);

			inputSteam.set(static_cast<uint32_t>(origPos));
		}

		uint32_t idSize = inputSteam.readUInt32BE();
		char* id = new char[idSize]();
		inputSteam.read(id, idSize);

		if (version == 1)
		{
			uint32_t compressMagic = inputSteam.readUInt32();

			// Sig:
			if (compressMagic == 0x3A676953)
			{
				hashSize = 64;
				inputSteam.read(hash, hashSize);
				compressMagic = inputSteam.readUInt32();
			}

			// SCLZ
			if (compressMagic == 0x5A4C4353)
			{
				signature = CompressionSignature::LZHAM;
			}
			// LZMA
			else
			{
				signature = CompressionSignature::LZMA;
			}

			inputSteam.set(inputSteam.tell() - 4);
		}

		CompressedSwfProps header = {
			id,
			idSize,

			metadata,
			metadataSize,

			static_cast<uint32_t>(signature),

			hash,
			hashSize,

			magic == 0x53430000
		};

		return header;
	}
}