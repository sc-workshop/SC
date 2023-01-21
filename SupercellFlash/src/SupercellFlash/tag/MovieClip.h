#pragma once

#include "SupercellFlash/common/DisplayObject.h"

namespace sc
{
	class SupercellSWF;

	struct MovieClipFrame
	{
		uint16_t elementsCount;
		std::string label;

		void load(SupercellSWF* swf);
	};

	struct MovieClipFrameElement
	{
		uint16_t instanceIndex;
		uint16_t matrixIndex;
		uint16_t colorTransformIndex;
	};

	struct DisplayObjectInstance
	{
		uint16_t id;
		uint8_t blend;
		std::string name;
	};

	struct ScalingGrid
	{
		float x;
		float y;
		float width;
		float height;
	};

	class MovieClip : public DisplayObject
	{
	public:
		MovieClip() { }
		virtual ~MovieClip() { }

	public:
		void load(SupercellSWF* swf, uint8_t tag);

	private:
		uint8_t m_frameRate = 24;

		std::vector<MovieClipFrameElement> m_frameElements;
		std::vector<DisplayObjectInstance> m_instances;

		std::vector<MovieClipFrame> m_frames;

		ScalingGrid* m_scalingGrid = nullptr;
		uint8_t m_matrixBankIndex = 0;
	};
}
