#pragma once

#include "Utils.h"
#include "Bytestream.hpp"

namespace sc {
	class ZSTD {
	public:
		static CompressionError decompress(IBinaryStream& inStream, IBinaryStream& outStream);
		static CompressionError compress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}
