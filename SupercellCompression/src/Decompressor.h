#pragma once

#include <cstdio>
#include <string>

#include "Signature.h"
#include "Utils.h"
#include "Signature.h"
#include "ByteStream.h"

namespace sc
{
	class Decompressor
	{
	public:
		/**
		 * Decompresses file and then stores it in cache, without need to decompress in the future.
		 *
		 * @param filepath: Path fo .sc file.
		 * @param outFilepath: Reference to string where path to cached will be placed.
		 */
		static CompressorError Decompressor::decompress(std::string filepath, std::string& outFilepath);

		/**
		 * Decompresses file. Can be used for memory streams or file streams. Files are not cached, so decompress process may be repeated.
		 *
		 * @param inStream: Input stream for reading.
		 * @param outStream: Output stream for writing.
		 */
		static CompressorError Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream);

		/**
		 * Decompress function for when you already have a header.
		 *
		 * @param inStream: Input stream for reading.
		 * @param outStream: Output stream for writing.
		 * @param header: SCSWF header.
		 */
		static CompressorError decompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps header);

		/**
		 * Reads information about the ss file. Contains information such as metadata, hash, compression method, and more.
		 *
		 * @param inStream: Input stream for reading.
		 */
		static CompressedSwfProps getHeader(IBinaryStream& inputSteam);

		/**
		 * Function to decompress assets like .csv or other compressed assets
		 *
		 * @param inStream: Input stream for reading.
		 * @param outStream: Output stream for writing.
		 */
		static CompressorError commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream);

		/**
		 * Function to decompress assets like .csv or other compressed assets in cases where you know exactly file signature.
		 *
		 * @param inStream: Input stream for reading.
		 * @param outStream: Output stream for writing.
		 * @param signature: File compress signature
		 */
		static CompressorError commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressionSignature signature);
	};
}
