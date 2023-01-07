#pragma once
#include "Utils.h"

#include <LzmaDec.h>

namespace sc {
	class LZMA {
	public:
		static CompressionErrs decompress(IBinaryStream& inStream, IBinaryStream& outStream);
		static CompressionErrs compress(IBinaryStream& inStream, IBinaryStream& outStream);

	private:
		static CompressionErrs decompressStream(CLzmaDec* state, SizeT unpackSize, IBinaryStream& inStream, IBinaryStream& outStream);
	};
}