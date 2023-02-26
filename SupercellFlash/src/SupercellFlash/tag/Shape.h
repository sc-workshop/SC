#pragma once

#include "SupercellFlash/common/DisplayObject.h"
#include "SupercellFlash/tag/ShapeDrawBitmapCommand.h"

namespace sc
{
	class SupercellSWF;
	class SWFStream;

	class Shape : public DisplayObject
	{
	public:
		Shape() { }
		virtual ~Shape() { }

	public:
		std::vector<ShapeDrawBitmapCommand> commands;

	public:
		void load(SupercellSWF* swf, uint8_t tag);
		void save(SupercellSWF* swf);
	};
}
