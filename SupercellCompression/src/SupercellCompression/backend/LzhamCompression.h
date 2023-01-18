#pragma once

#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/ByteStream.hpp"

namespace sc
{
	class LZHAM
	{
	public:
		static CompressionError compress(BinaryStream& inStream, BinaryStream& outStream);
		static CompressionError decompress(BinaryStream& inStream, BinaryStream& outStream);
	};
}