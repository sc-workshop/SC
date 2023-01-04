#pragma once

#include "Utils.h"

namespace sc {
	class LZHAM {
	public:
		static CompressErrs decompress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}