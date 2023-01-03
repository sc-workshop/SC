#pragma once

#include "Utils.h"

namespace sc {
	class ZSTD {
	public:
		static COMPRESSION_ERROR decompress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}
