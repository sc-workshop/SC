#include "Decompressor.h"
#include "Signature.h"
#include "Cache.h"
#include "Utils.h"
#include "Endian.h"

#include "Lzma.h"
#include "Zstd.h"

#include <iostream>

namespace sc
{ 
	// Decompress SC file
	DecompressorErrs Decompressor::decompress(std::string filepath, std::string& outFilepath)
	{
		if (!Utils::endsWith(filepath, ".sc")) {
			return DecompressorErrs::WRONG_FILE_ERROR;
		}

		FILE* inFile = fopen(filepath.c_str(), "rb");
		unsigned int fileSize = Utils::fileSize(inFile);
		if (inFile == NULL || fileSize <= 0)
			return DecompressorErrs::FILE_READ_ERROR;

		ScFileStream inputSteam = ScFileStream(inFile);

		char* hash;
		uint32_t hashSize;
		CompressionSignatures signature;

		int headerRes = getHeader(inputSteam, hash, hashSize, signature);
		if (headerRes != 0) {
			return DecompressorErrs::WRONG_FILE_ERROR;
		}

		outFilepath = SwfCache::getTempPath(filepath);
		bool fileInCache = SwfCache::exist(filepath, hash, fileSize);
		if (fileInCache) {
			return DecompressorErrs::OK;
		}
		else {
			SwfCache::addData(filepath, hash, hashSize, fileSize);
		}
			
		FILE* outFile = fopen(outFilepath.c_str(), "wb");
		if (outFile == NULL)
			return DecompressorErrs::FILE_WRITE_ERROR;

		ScFileStream outputStream = ScFileStream(outFile);

		return decompress(inputSteam, outputStream, signature);
	}

	int Decompressor::getHeader(
		IBinaryStream& inputSteam,
		char* &hash, uint32_t &hashSize,
		CompressionSignatures &signature) {
		// Header reading
		// Check for SC file header 
		int magic;
		inputSteam.read(&magic, sizeof(magic));
		if (magic != 0x4353)
			return 1;

		// Version of SC file
		unsigned short version;

		inputSteam.read(&version, sizeof(version));
		version = SwapEndian<short>(version);
		// if version is 4, then it already have a signature index and there is no need to 'brutforce' it  
		if (version == 4) {
			unsigned int signatureIndex;
			inputSteam.read(&signatureIndex, sizeof(signatureIndex));
			signatureIndex = SwapEndian<int>(signatureIndex);
			signature = static_cast<CompressionSignatures>(signatureIndex);

			// Metadata process
			size_t origPos = inputSteam.tell();

			inputSteam.set(inputSteam.size() - 4);
			uint32_t metadataSize = 0;
			inputSteam.read(&metadataSize, sizeof(metadataSize));
			metadataSize = SwapEndian<uint32_t>(metadataSize);

			inputSteam.set(origPos);
			inputSteam.setEof(static_cast<__int64>(metadataSize) + 9);
		}

		inputSteam.read(&hashSize, sizeof(hashSize));
		hashSize = SwapEndian<int>(hashSize);

		hash = new char[hashSize]();
		inputSteam.read(hash, hashSize);

		if (version != 4) {
			long origPosition = inputSteam.tell();
			uint32_t compressMagic;
			inputSteam.read(&compressMagic, sizeof(compressMagic));
			signature = getSignature(compressMagic);
			inputSteam.set(origPosition);
		}

		return 0;
	}

	DecompressorErrs Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressionSignatures signature) {
		CompressErrs res;

		switch (signature)
		{
		case CompressionSignatures::LZMA:
			res = LZMA::decompress(inStream, outStream);
			break;
		case CompressionSignatures::ZSTD:
			res = ZSTD::decompress(inStream, outStream);
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
}
