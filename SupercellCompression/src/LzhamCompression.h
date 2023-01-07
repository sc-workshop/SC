#pragma once

#include "Utils.h"

namespace sc {
	class LZHAM {
	public:
		static CompressionErrs decompress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}