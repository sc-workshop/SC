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

		/*Vectors*/
	public:
		std::vector<MovieClipFrameElement> frameElements;
		std::vector<DisplayObjectInstance> instances;
		std::vector<MovieClipFrame> frames;

		/* Getters */
	public:
		uint8_t frameRate() { return m_frameRate; }
		ScalingGrid scalingGrid() { return *m_scalingGrid; }
		uint8_t matrixBankIndex() { return m_matrixBankIndex; }

	public:
		void load(SupercellSWF* swf, uint8_t tag);

	private:
		uint8_t m_frameRate = 24;

		ScalingGrid* m_scalingGrid = nullptr;
		uint8_t m_matrixBankIndex = 0;
	};
}
