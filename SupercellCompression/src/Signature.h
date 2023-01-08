#pragma once
#include "Utils.h"

namespace sc {
	enum CompressionSignatures : uint32_t {
		NONE_COMPRESSION = 0,
		LZMA_COMPRESSION = 1,
		LZHAM_COMPRESSION = 2,
		ZSTD_COMRESSION = 3
	};

	inline CompressionSignatures getSignature(uint32_t magic) {
		switch (magic)
		{
		case 0x0400005D:
		case 0x0400005E:
			return CompressionSignatures::LZMA_COMPRESSION;
		case 0x5A4C4353:
			return CompressionSignatures::LZHAM_COMPRESSION;
		case 0xFD2FB528:
			return CompressionSignatures::ZSTD_COMRESSION;
		default:
			return CompressionSignatures::NONE_COMPRESSION;
		}
	}
}
