#pragma once

#include <cstdio>
#include <string>

#include "Signature.h"
#include "Utils.h"
#include "Signature.h"

namespace sc
{
	class Decompressor
	{
	public:
		static DECOMPRESSOR_ERROR Decompressor::decompress(std::string filepath, std::string& outFilepath);
		
	private:
		static DECOMPRESSOR_ERROR decompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressionSignatures signature);
		static int Decompressor::getHeader(IBinaryStream& inputSteam, char*& hash, uint32_t& hashSize, CompressionSignatures& signature);
		
	};
}
