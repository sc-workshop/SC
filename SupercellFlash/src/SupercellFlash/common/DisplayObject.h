#pragma once

#include <cstdint>

namespace sc
{
	struct Matrix2x3;
	struct ColorTransform;

	class DisplayObject
	{
	public:
		virtual void render() { }

	protected:
		uint16_t m_id = 0;

		Matrix2x3* m_matrix;
		ColorTransform* m_colorTransform;
	};
}
