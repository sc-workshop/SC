#pragma once

#include <LzmaDec.h>

#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/ByteStream.hpp"

namespace sc
{
	class LZMA
	{
	public:
		static CompressionError decompress(BinaryStream& inStream, BinaryStream& outStream);
		static CompressionError compress(BinaryStream& inStream, BinaryStream& outStream);

	private:
		static CompressionError decompressStream(CLzmaDec* state, SizeT unpackSize, BinaryStream& inStream, BinaryStream& outStream);
	};
}