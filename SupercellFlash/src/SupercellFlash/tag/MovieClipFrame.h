#pragma once

#include <string>
#include "../common/SwfStream.h"

namespace sc
{
	struct MovieClipFrame
	{
		uint16_t elementsCount;
		std::string label;

		void load(SupercellSWF* swf);
		void save(SupercellSWF* movieClipStream);
	};
}
