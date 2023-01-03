#include "SupercellSWF/MovieClip.h"

namespace sc
{
	void MovieClip::load(SupercellSWF* swf, int tag)
	{
		m_id = swf->readUnsignedShort();

		m_frameRate = swf->readUnsignedByte();

		m_framesCount = swf->readUnsignedShort();
		m_frames = new MovieClipFrame[m_framesCount];

		m_frameElementsCount = swf->readInt() * 3;
		m_frameElements = new int[m_frameElementsCount];

		for (int i = 0; i < m_frameElementsCount; i += 3)
		{
			m_frameElements[i + 0] = swf->readUnsignedShort(); // instance index
			m_frameElements[i + 1] = swf->readUnsignedShort(); // matrix index
			m_frameElements[i + 2] = swf->readUnsignedShort(); // color transform index
		}

		m_instancesCount = swf->readUnsignedShort();
	}
}
