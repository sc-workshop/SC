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
	DecompressorErrs Decompressor::decompress(std::string filepath, std::string& outFilepath)
	{
		if (!Utils::endsWith(filepath, ".sc")) {
			return DecompressorErrs::WRONG_FILE_ERROR;
		}

		if (!Utils::fileExist(filepath)) 
			return DecompressorErrs::FILE_READ_ERROR;

		FILE* inFile = fopen(filepath.c_str(), "rb");
		ScFileStream inputSteam = ScFileStream(inFile);
		uint32_t fileSize = Utils::fileSize(inFile);

		CompressedSwfProps header = getHeader(inputSteam);
		if (!header.ok) {
			return DecompressorErrs::WRONG_FILE_ERROR;
		}

		outFilepath = SwfCache::getTempPath(filepath);
		bool fileInCache = SwfCache::exist(filepath, header.id, fileSize);
		if (fileInCache) {
			return DecompressorErrs::OK;
		}
		else {
#ifndef SC_DEBUG
			SwfCache::addData(filepath, header, fileSize);
#endif // !SC_DEBUG
		}
			
		FILE* outFile = fopen(outFilepath.c_str(), "wb");
		if (outFile == NULL)
			return DecompressorErrs::FILE_WRITE_ERROR;

		ScFileStream outputStream = ScFileStream(outFile);

		DecompressorErrs res = decompress(inputSteam, outputStream, header);

		inputSteam.close();
		outputStream.close();

		return res;
	}

	DecompressorErrs Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream)
	{
		CompressedSwfProps header = getHeader(inStream);
		if (!header.ok)
			return DecompressorErrs::WRONG_FILE_ERROR;
		
		decompress(inStream, outStream, header);

		return DecompressorErrs::OK;
	}

	DecompressorErrs Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps header) {
		CompressErrs res;

		switch (header.signature)
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
			char* dataBuffer = new char[size]();
			inStream.read(dataBuffer, size);
			outStream.write(dataBuffer, size);

			res = CompressErrs::OK;
			break;
		}

		return res == CompressErrs::OK ? DecompressorErrs::OK : DecompressorErrs::DECOMPRESS_ERROR;
	}

	DecompressorErrs Decompressor::commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		CompressErrs res;

		inStream.set(0);
		uint32_t magic;
		inStream.read(&magic, sizeof(magic));
		inStream.set(0);

		uint32_t signature = getSignatureIndex(magic);

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
			char* dataBuffer = new char[size]();
			inStream.read(dataBuffer, size);
			outStream.write(dataBuffer, size);

			res = CompressErrs::OK;
			break;
		}

		return res == CompressErrs::OK ? DecompressorErrs::OK : DecompressorErrs::DECOMPRESS_ERROR;
	}

	CompressedSwfProps Decompressor::getHeader(IBinaryStream& inputSteam) {

		// .sc file header
		int magic;
		inputSteam.read(&magic, sizeof(magic));

		// Version of .sc file
		uint16_t version;
		inputSteam.read(&version, sizeof(version));
		version = SwapEndian<short>(version);

		uint32_t signature;
		char* metadata{};
		uint32_t metadataSize = 0;
		char* hash{};
		uint32_t hashSize = 0;

		// if version is 4, then it already have a signature index and there is no need to 'brutforce' it  
		if (version == 4) {
			inputSteam.read(&signature, sizeof(signature));
			signature = SwapEndian<uint32_t>(signature);
			signature = static_cast<CompressionSignatures>(signature);

			// Metadata process
			size_t origPos = inputSteam.tell();
			inputSteam.set(static_cast<uint32_t>(inputSteam.size()) - 4);
			inputSteam.read(&metadataSize, sizeof(metadataSize));
			metadataSize = SwapEndian<uint32_t>(metadataSize);

			metadata = new char[metadataSize]();
			inputSteam.set(static_cast<uint32_t>(inputSteam.size() - (metadataSize + 4)));
			inputSteam.read(metadata, metadataSize);

			inputSteam.set(static_cast<uint32_t>(origPos));
			// inputSteam.setEof(static_cast<__int64>(metadataSize) + 9);
		}
		uint32_t idSize;
		inputSteam.read(&idSize, sizeof(idSize));
		idSize = SwapEndian<uint32_t>(idSize);

		char *id = new char[idSize]();
		inputSteam.read(id, idSize);

		if (version != 4) {
			long origPosition = inputSteam.tell();
			uint32_t compressMagic;
			inputSteam.read(&compressMagic, sizeof(compressMagic));

			// If SIG
			if (compressMagic == 0x3A676953) {
				hashSize = 64;
				inputSteam.read(hash, hashSize);
				origPosition += 4 + hashSize;
				inputSteam.read(&compressMagic, sizeof(compressMagic));
			}

			signature = getSignatureIndex(compressMagic);
			inputSteam.set(origPosition);
		}

		CompressedSwfProps header = {
			id,
			idSize,
			hash,
			hashSize,
			metadata,
			metadataSize,
			signature,
			magic == 0x4353
		};

		return header;
	}

}
