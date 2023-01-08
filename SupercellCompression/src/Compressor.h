#pragma once

#include "Utils.h"

#include <string>

namespace sc
{
	class Compressor
	{
	public:
		static CompressorErrs compress(std::string inputFilepath, std::string outFilepath, CompressionSignatures signature);
		static CompressorErrs compress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps& header);
		static CompressorErrs commonCompress(IBinaryStream& inStream, IBinaryStream& outStream, uint32_t signatureIndex);
	};
}
