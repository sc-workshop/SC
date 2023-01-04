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
		/**
		 * Decompresses file and then stores it in cache, without need to decompress in the future.
		 *
		 * @param filepath: Path fo .sc file.
		 * @param outFilepath: Reference to string where path to cached will be placed.
		 */
		static DecompressorErrs Decompressor::decompress(std::string filepath, std::string& outFilepath);

		/**
		 * Decompresses file. Can be used for memory streams or file streams. Files are not cached, so decompress process may be repeated.
		 *
		 * @param inStream: Input stream for reading.
		 * @param outStream: Output stream for writing.
		 */
		static DecompressorErrs Decompressor::decompress(IBinaryStream& inStream, IBinaryStream& outStream);

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
		static DecompressorErrs commonDecompress(IBinaryStream& inStream, IBinaryStream& outStream);

	private:
		static DecompressorErrs decompress(IBinaryStream& inStream, IBinaryStream& outStream, CompressedSwfProps header);
	};
}
