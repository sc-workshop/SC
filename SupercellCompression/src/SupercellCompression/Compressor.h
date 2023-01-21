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
		* Compress .sc file.
		*/
		static CompressorError compress(const std::string& inputFilepath, std::string outFilepath, CompressionSignature signature);

		/*
		* Compress .sc file data from stream.
		*/
		static CompressorError compress(BinaryStream& inStream, BinaryStream& outStream, CompressionSignature signature);

		/*
		* Compress .sc file with header properties.
		*/
		static CompressorError compress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps& header);

		/*
		* Compress common file data.
		*/
		static CompressorError commonCompress(BinaryStream& inStream, BinaryStream& outStream, CompressionSignature signature);

	};
}
