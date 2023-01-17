#pragma once

#include "Utils.h"
#include "Bytestream.hpp"

namespace sc
{
	class LZHAM
	{
	public:
		static CompressionError compress(IBinaryStream& inStream, IBinaryStream& outStream);
		static CompressionError decompress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}