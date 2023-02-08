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
	CompressorError Decompressor::decompress(std::string filepath, std::string& outFilepath, CompressedSwfProps *header)
	{
		if (!Utils::endsWith(filepath, ".sc")) {
			return CompressorError::WRONG_FILE_ERROR;
		}

		if (!Utils::fileExist(filepath))
			return CompressorError::FILE_READ_ERROR;

		FILE* inFile = fopen(filepath.c_str(), "rb");
		if (inFile == NULL)
			return CompressorError::FILE_READ_ERROR;

		FileStream inputSteam = FileStream(inFile);
		uint32_t fileSize = Utils::fileSize(inFile);

		*header = getHeader(inputSteam);

		outFilepath = SwfCache::getTempPath(filepath);
		bool fileInCache = SwfCache::exist(filepath, header->id, fileSize);
		if (fileInCache)
		{
			return CompressorError::OK;
		}

		FILE* outFile = fopen(outFilepath.c_str(), "wb");
		if (outFile == NULL)
			return CompressorError::FILE_WRITE_ERROR;

		FileStream outputStream = FileStream(outFile);

		CompressorError res = decompress(inputSteam, outputStream, *header);

		inputSteam.close();
		outputStream.close();

		if (res == CompressorError::OK && !fileInCache)
		{
#ifndef DISABLE_CACHE
			SwfCache::addData(filepath, *header, fileSize);
#endif
		}

		return res;
	}

	CompressorError Decompressor::decompress(BinaryStream& inStream, BinaryStream& outStream)
	{
		CompressedSwfProps header = getHeader(inStream);

		return decompress(inStream, outStream, header);
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

	CompressorError Decompressor::decompress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps header) {
		inStream.setEof(static_cast<uint32_t>(header.metadata.empty() ? 0 : header.metadata.size() + 9));

		CompressorError res = commonDecompress(inStream, outStream, static_cast<CompressionSignature>(header.signature));

		inStream.setEof(0);

		return res;
	}

	CompressorError Decompressor::commonDecompress(BinaryStream& inStream, BinaryStream& outStream) {
		inStream.set(0);
		uint32_t magic;
		inStream.read(&magic, sizeof(magic));
		inStream.set(0);

		CompressionSignature signature;

		if (magic == 0x3A676953) {
			inStream.skip(64);
			inStream.read(&magic, sizeof(magic));
		}

		signature = getSignature(magic);

		return commonDecompress(inStream, outStream, signature);
	}

	CompressedSwfProps Decompressor::getHeader(BinaryStream& inputSteam) {
		CompressedSwfProps header;

		// .sc file header
		uint32_t magic = inputSteam.readUInt32BE();

		switch (magic)
		{
		case 0x53430000: // SC
			break;
		case 0x3A676953: // SIGN (compressed csv)
			inputSteam.read(header.sign.data(), 64);
			return header;
		default:
			return header;
		}

		// Version of .sc file
		uint32_t version = static_cast<uint32_t>(inputSteam.readUInt16BE());

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
			header.signature = static_cast<uint32_t>(CompressionSignature::ZSTD);
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
				header.signature = static_cast<uint32_t>(CompressionSignature::LZHAM);
			}

			// LZMA
			else
			{
				header.signature = static_cast<uint32_t>(CompressionSignature::LZMA);
			}

			inputSteam.set(inputSteam.tell() - 4);
		}

		return header;
	}
}