#pragma once

#include <string>

#include "Signature.h"
#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/ByteStream.hpp"

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
		* Compresses a filedata from input stream to out stream with given compression signature
		*/
		static CompressorError commonCompress(BinaryStream& inStream, BinaryStream& outStream, CompressionSignature signature);

		/*
		* Compresses a filedata from input stream to out stream with given header setting
		*/
		static CompressorError compress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps& header);

	};
}
