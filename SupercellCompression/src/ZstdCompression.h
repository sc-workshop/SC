#pragma once

#include "Utils.h"

namespace sc {
	class ZSTD {
	public:
		static CompressErrs decompress(IBinaryStream& inStream, IBinaryStream& outStream);
	};
}
