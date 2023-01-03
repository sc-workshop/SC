#pragma once
#include "Utils.h"

#include "LZMA/LzmaDec.h"

namespace sc {
	class LZMA {
	public:
		static COMPRESSION_ERROR decompress(IBinaryStream& inStream, IBinaryStream& outStream);

	private:
		static COMPRESSION_ERROR decompressStream(CLzmaDec* state, SizeT unpackSize, IBinaryStream& inStream, IBinaryStream& outStream);
	};
}