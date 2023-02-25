#pragma once

#include <string>

namespace sc
{
	class BufferStream;
	class SupercellSWF;

	struct MovieClipFrame
	{
		uint16_t elementsCount;
		std::string label;

		void load(SupercellSWF* swf);
		void save(BufferStream& movieClipStream);
	};
}
