#pragma once

#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/ByteStream.hpp"

namespace sc {
	class ZSTD {
	public:
		static CompressionError decompress(BinaryStream& inStream, BinaryStream& outStream);
		static CompressionError compress(BinaryStream& inStream, BinaryStream& outStream);
	};
}
