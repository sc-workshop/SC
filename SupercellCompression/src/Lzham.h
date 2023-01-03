#pragma once

#include "Utils.h"

namespace sc {
	class LZHAM {
	public:
		static int decompress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}