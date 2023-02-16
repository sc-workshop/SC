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
		static CompressorError decompress(std::string filepath, std::string& outFilepath);

		/**
		 * Decompress file and then store it in cache, without need to decompress in the future. With header props.
		 */
		static CompressorError decompress(std::string filepath, std::string& outFilepath, CompressedSwfProps* header);

		/**
		 * Decompress file from stream.
		 */
		static CompressorError decompress(BinaryStream& inStream, BinaryStream& outStream);

		/**
		 * Decompress file with header properties.
		 */
		static CompressorError decompress(BinaryStream& inStream, BinaryStream& outStream, CompressedSwfProps header);

		/**
		 * Decompress assets like .csv or other compressed assets
		 */
		static CompressorError commonDecompress(BinaryStream& inStream, BinaryStream& outStream);

		/**
		 * Reads information about sc file. Contains information such as metadata, sign, compression method.
		 */
		static CompressedSwfProps getHeader(BinaryStream& inputSteam);

	private:
		static CompressorError commonDecompress(BinaryStream& inStream, BinaryStream& outStream, CompressionSignature signature);
	};
}
