#pragma once

#include <string>

#include "Utils.h"
#include "ByteStream.h"

namespace sc
{
	class Compressor
	{
	public:
		/*
		* Compresses a file at given path and with given compression signature
		*/
		static CompressorError compress(const std::string& inputFilepath, std::string outFilepath, CompressionSignature signature);

		/*
		* Compresses a filedata from input stream to out stream with given header setting
		*/
		static CompressorError compress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps& header);

		/*
		* Compresses a filedata from input stream to out stream with given compression signature
		*/
		static CompressorError commonCompress(IBinaryStream& inStream, IBinaryStream& outStream, uint32_t signatureIndex);
	};
}
