#pragma once
#include "Utils.h"

#include <LzmaDec.h>

namespace sc {
	class LZMA {
	public:
		static CompressErrs decompress(IBinaryStream& inStream, IBinaryStream& outStream);

	private:
		static CompressErrs decompressStream(CLzmaDec* state, SizeT unpackSize, IBinaryStream& inStream, IBinaryStream& outStream);
	};
}