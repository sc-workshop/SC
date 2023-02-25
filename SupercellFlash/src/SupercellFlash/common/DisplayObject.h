#pragma once

#include <cstdint>

namespace sc
{
	struct Matrix2x3;
	struct ColorTransform;

	class DisplayObject
	{
	public:
		DisplayObject() { }
		virtual ~DisplayObject() { }

		uint16_t id() { return m_id; }
		void id(uint16_t id) { m_id = id; }

	protected:
		uint16_t m_id = 0;

		Matrix2x3* m_matrix = nullptr;
		ColorTransform* m_colorTransform = nullptr;
	};
}
