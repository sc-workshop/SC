#pragma once

#include "SupercellSWF/SupercellSWF.h"

namespace sc
{
	class MovieClip
	{
	public:
		void load(SupercellSWF* swf, int tag);

	private:
		int m_id;
		int m_frameRate;

		int m_framesCount;
		MovieClipFrame* m_frames;

		int m_frameElementsCount;
		int* m_frameElements;

		int m_instancesCount;
		int* m_instanceIds;
		int* m_instanceBlends;
		std::string* m_instanceNames;
	};

	struct MovieClipFrame
	{

	};
}
