#include "Decompressor.h"
#include "Signature.h"
#include "Cache.h"
#include "Utils.h"
#include "Endian.h"

#include "LzmaCompression.h"
#include "LzhamCompression.h"
#include "ZstdCompression.h"

#include <iostream>

namespace sc
{
	// Decompress SC file
	CompressorErrs Decompressor::decompress(std::string filepath, std::string& outFilepath)
	{
		if (!Utils::endsWith(filepath, ".sc")) {
			return CompressorErrs::WRONG_FILE_ERROR;
		}

		if (!Utils::fileExist(filepath))
			return CompressorErrs::FILE_READ_ERROR;

		FILE* inFile = fopen(filepath.c_str(), "rb");
		ScFileStream inputSteam = ScFileStream(inFile);
		uint32_t fileSize = Utils::fileSize(inFile);

		CompressedSwfProps header = getHeader(inputSteam);
		if (!header.ok) {
			return CompressorErrs::WRONG_FILE_ERROR;
		}

		outFilepath = SwfCache::getTempPath(filepath);
		bool fileInCache = SwfCache::exist(filepath, header.id, fileSize);
		if (fileInCache) {
			return CompressorErrs::OK;
		}
		else {
#ifndef SC_DEBUG
			SwfCache::addData(filepath, header, fileSize);
#endif // !SC_DEBUG
		}

		FILE* outFile = fopen(outFilepath.c_str(), "wb");
		if (outFile == NULL)
			return CompressorErrs::FILE_WRITE_ERROR;

		ScFileStream outputStream = ScFileStream(outFile);

		CompressorErrs res = decompress(inputSteam, outputStream, header);

		inputSteam.close();
		outputStream.close();

		return res;
	}

	CompressorErrs Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream)
	{
		CompressedSwfProps header = getHeader(inStream);
		if (!header.ok)
			return CompressorErrs::WRONG_FILE_ERROR;

		return decompress(inStream, outStream, header);
	}

	CompressorErrs Decompressor::commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressionSignatures signature) {
		CompressionErrs res;

		switch (signature)
		{
		case CompressionSignatures::LZMA_COMPRESSION:
			res = LZMA::decompress(inStream, outStream);
			break;
		case CompressionSignatures::ZSTD_COMRESSION:
			res = ZSTD::decompress(inStream, outStream);
			break;
		case CompressionSignatures::LZHAM_COMPRESSION:
			res = LZHAM::decompress(inStream, outStream);
			break;
		default:
			size_t size = inStream.size() - inStream.tell();
			void* dataBuffer = malloc(size);
			inStream.read(dataBuffer, size);
			outStream.write(dataBuffer, size);
			free(dataBuffer);
			res = CompressionErrs::OK;
			break;
		}

		return res == CompressionErrs::OK ? CompressorErrs::OK : CompressorErrs::DECOMPRESS_ERROR;
	}

	CompressorErrs Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps header) {
		inStream.setEof(static_cast<__int64>(header.metadataSize) + header.metadataSize != 0 ? 9 : 0);

		CompressorErrs res = commonDecompress(inStream, outStream, static_cast<CompressionSignatures>(header.signature));

		inStream.setEof(0);

		return res;
	}

	CompressorErrs Decompressor::commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		inStream.set(0);
		uint32_t magic;
		inStream.read(&magic, sizeof(magic));
		inStream.set(0);

		CompressionSignatures signature = getSignature(magic);

		return commonDecompress(inStream, outStream, signature);
	}

	CompressedSwfProps Decompressor::getHeader(IBinaryStream& inputSteam) {
		// .sc file header
		uint32_t magic = inputSteam.readUInt32BE();

		// Version of .sc file
		uint16_t version = inputSteam.readUInt16BE();

		uint32_t signature = 0;
		char* metadata{};
		uint32_t metadataSize = 0;
		char* hash{};
		uint32_t hashSize = 0;

		if (version == 3) {
			signature = CompressionSignatures::ZSTD_COMRESSION;
		}
		else if (version == 4) {
			signature = static_cast<CompressionSignatures>(inputSteam.readUInt32BE());

			size_t origPos = inputSteam.tell();
			inputSteam.set(static_cast<uint32_t>(inputSteam.size()) - 4);
			metadataSize = inputSteam.readUInt32BE();

			metadata = new char[metadataSize]();
			inputSteam.set(static_cast<uint32_t>(inputSteam.size() - (metadataSize + 4)));
			inputSteam.read(metadata, metadataSize);

			inputSteam.set(static_cast<uint32_t>(origPos));
			//inputSteam.setEof(static_cast<__int64>(metadataSize) + 9);
		}

		uint32_t idSize = inputSteam.readUInt32BE();
		char* id = new char[idSize]();
		inputSteam.read(id, idSize);

		if (version == 1) {
			auto pos = inputSteam.tell();
			uint32_t compressMagic = inputSteam.readUInt32();

			// SIG
			if (compressMagic == 0x3A676953) {
				hashSize = 64;
				inputSteam.read(hash, hashSize);
				compressMagic = inputSteam.readUInt32();
			}

			// SCLZ
			if (compressMagic == 0x5A4C4353) {
				signature = CompressionSignatures::LZHAM_COMPRESSION;
			}
			else {
				signature = CompressionSignatures::LZMA_COMPRESSION;
			}

			inputSteam.set(inputSteam.tell() - 4);
		}

		CompressedSwfProps header = {
			id,
			idSize,

			metadata,
			metadataSize,

			signature,

			hash,
			hashSize,

			magic == 0x53430000
		};

		return header;
	}
}