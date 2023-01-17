#pragma once

#include <Bytestream.h>
#include <vector>

#include <common/Tag.h>

namespace sc
{
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
		void loadTag(IBinaryStream* stream, uint8_t tag, int* pointsOffset, std::vector<ShapeDrawBitmapCommandVertex>& vertices);
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

	class Shape: public ScTag
	{
	public:
		void loadTag(IBinaryStream* stream, uint8_t tag);
		uint16_t getTag();

		std::vector<ShapeDrawBitmapCommand> commands;
		std::vector<ShapeDrawBitmapCommandVertex> vertices;
	};

	
}
