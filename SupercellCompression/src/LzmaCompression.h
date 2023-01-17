#pragma once

#include <LzmaDec.h>

#include "Utils.h"
#include "Bytestream.h"

namespace sc
{
	class LZMA
	{
	public:
		static CompressionError decompress(IBinaryStream& inStream, IBinaryStream& outStream);
		static CompressionError compress(IBinaryStream& inStream, IBinaryStream& outStream);

	private:
		static CompressionError decompressStream(CLzmaDec* state, SizeT unpackSize, IBinaryStream& inStream, IBinaryStream& outStream);
	};
}