#pragma once

#include "Utils.h"
#include "Bytestream.h"

namespace sc {
	class LZHAM {
	public:
		static CompressionErrs compress(IBinaryStream& inStream, IBinaryStream& outStream);
		static CompressionErrs decompress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}