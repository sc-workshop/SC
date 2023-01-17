#pragma once
#include "Utils.h"

namespace sc
{
	enum class CompressionSignature : uint32_t
	{
		NONE = 0,

		LZMA,
		LZHAM,
		ZSTD,
	};

	inline CompressionSignature getSignature(uint32_t magic)
	{
		switch (magic)
		{
		case 0x0400005D:
		case 0x0400005E:
			return CompressionSignature::LZMA;

		case 0x5A4C4353:
			return CompressionSignature::LZHAM;

		case 0xFD2FB528:
			return CompressionSignature::ZSTD;

		default:
			return CompressionSignature::NONE;
		}
	}
}
