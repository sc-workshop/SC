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

		/* Functions */
	public:
		void load(SupercellSWF* swf, uint8_t tag);

		/* Vectors */
	public:
		std::vector<ShapeDrawBitmapCommandVertex> vertices;

		/* Getters */
	public:
		uint8_t textureIndex() { return m_textureIndex; }

		/* Setters */
	public:
		void textureIndex(uint8_t index) { m_textureIndex = index; }

	private:
		uint8_t m_textureIndex = 0;
	};

	class Shape : public DisplayObject
	{
	public:
		Shape() { }
		virtual ~Shape() { }

	public:
		std::vector<ShapeDrawBitmapCommand> commands;

	public:
		void load(SupercellSWF* swf, uint8_t tag);
	};
}
