#pragma once
#include "Utils.h"

namespace sc {
	enum CompressionSignatures {
		NONE,
		LZMA,
		LZHAM,
		ZSTD,
		SIG // Idk about this. They probably cut it out completely, but let it be.
	};

	inline CompressionSignatures getSignature(uint32_t magic) {
		switch (magic)
		{
		case 0x0400005D:
		case 0x0400005E:
			return CompressionSignatures::LZMA;
		case 0x5A4C4353:
			return CompressionSignatures::LZHAM;
		case 0xFD2FB528:
			return CompressionSignatures::ZSTD;
		case 0x3A676953:
			return CompressionSignatures::SIG;
		default:
			return CompressionSignatures::NONE;
		}
	}
}
