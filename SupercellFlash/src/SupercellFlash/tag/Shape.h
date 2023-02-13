#pragma once

#include "SupercellFlash/common/DisplayObject.h"

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
		ShapeDrawBitmapCommand() { }
		virtual ~ShapeDrawBitmapCommand() { }

	public:
		void load(SupercellSWF* swf, uint8_t tag);

	public:
		std::vector<ShapeDrawBitmapCommandVertex> m_vertices;

	private:
		uint8_t m_textureIndex = 0;
		
	};

	class Shape : public DisplayObject
	{
	public:
		Shape() { }
		virtual ~Shape() { }

	public:
		void load(SupercellSWF* swf, uint8_t tag);

		std::vector<ShapeDrawBitmapCommand> m_commands;
	};
}
