#pragma once

#include <cstdint>

namespace sc
{
	struct ColorTransform
	{
		uint8_t redAdd = 0;
		uint8_t greenAdd = 0;
		uint8_t blueAdd = 0;

		float alphaMul = 1.0f;
		float redMul = 1.0f;
		float greenMul = 1.0f;
		float blueMul = 1.0f;
	};
}
