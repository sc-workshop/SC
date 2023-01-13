#pragma once

#include "Utils.h"
#include "Bytestream.h"

#include <string>

namespace sc
{
	class Compressor
	{
	public:
		/*
		* Compresses a file at given path and with given compression signature
		*/
		static CompressorErrs compress(std::string inputFilepath, std::string outFilepath, CompressionSignatures signature);

		/*
		* Compresses a filedata from input stream to out stream with given header setting
		*/
		static CompressorErrs compress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps& header);

		/*
		* Compresses a filedata from input stream to out stream with given compression signature
		*/
		static CompressorErrs commonCompress(IBinaryStream& inStream, IBinaryStream& outStream, uint32_t signatureIndex);
	};
}
