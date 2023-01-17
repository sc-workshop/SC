#pragma once
#include <stdint.h>
#include <vector>
#include "Tag.h"

namespace sc
{
	class SupercellSWF;

	struct ShapeDrawBitmapCommandVertex
	{
		float x;
		float y;

		float u;
		float v;
	};

	class ShapeDrawBitmapCommand
	{
	public:
		void load(SupercellSWF* swf, uint8_t tag, int* pointsOffset, std::vector<ShapeDrawBitmapCommandVertex>& vertices);
		uint16_t getTag();

		bool rectangle() { return m_rectangle; };
		bool normalized() { return m_normalized; }
		uint8_t pointsCount() { return m_pointsCount; }

	private:
		bool m_rectangle;
		bool m_normalized;

		uint8_t m_textureIndex;
		uint8_t m_pointsCount;
	};

	class Shape : public ScTag
	{
	public:
		void load(SupercellSWF* swf, uint8_t tag);
		uint8_t getTag();

	private:
		std::vector<ShapeDrawBitmapCommand> m_commands;
		std::vector<ShapeDrawBitmapCommandVertex> m_vertices;
	};
}
