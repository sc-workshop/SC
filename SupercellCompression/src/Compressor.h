#pragma once

#include "Utils.h"

#include <string>

namespace sc
{
	enum class CompressPressets {
		FAST,
		NORMAL
	};

	class Compressor
	{
	public:
		static CompressorErrs compress(std::string inputFilepath, std::string outFilepath, CompressPressets presset);
		static CompressorErrs compress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps& header);
	};
}
