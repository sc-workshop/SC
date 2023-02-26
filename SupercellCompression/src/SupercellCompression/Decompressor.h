#pragma once

#include <cstdio>
#include <string>

#include "Signature.h"

#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/ByteStream.hpp"

namespace sc
{
	class Decompressor
	{
	public:
		/**
		 * Decompress file and then store it in cache, without need to decompress in the future.
		 */
		static CompressorError decompress(const std::string& filepath, std::string& outFilepath, std::vector<uint8_t>* metadata);

		/**
		 * Decompress file from stream.
		 */
		static CompressorError decompress( BinaryStream& inStream,  BinaryStream& outStream, CompressedSwfProps* header);

		/**
		 * Decompress assets like .csv or other compressed assets
		 */
		static CompressorError commonDecompress( BinaryStream& inStream,  BinaryStream& outStream);

	private:
		static CompressedSwfProps getHeader( BinaryStream& inputSteam);
		static CompressorError decompress( BinaryStream& inStream,  BinaryStream& outStream, CompressedSwfProps header);
		static CompressorError commonDecompress( BinaryStream& inStream,  BinaryStream& outStream, CompressionSignature signature);
	};
}
