#include "SupercellFlash/SupercellSWF.h"
#include "SupercellFlash/tag/MovieClip.h"

namespace sc
{
	void MovieClipFrame::load(SupercellSWF* swf)
	{
		elementsCount = swf->readUnsignedShort();
		label = swf->readAscii();
	}

	void MovieClip::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();
		m_frameRate = swf->readUnsignedByte();

		uint16_t framesCount = swf->readUnsignedShort();
		m_frames = std::vector<MovieClipFrame>(framesCount);

		if (tag == 3 || tag == 14)
			throw std::runtime_error("TAG_MOVIE_CLIP and TAG_MOVIE_CLIP_4 is unsupported");

		int32_t frameElementsCount = swf->readInt();
		m_frameElements = std::vector<MovieClipFrameElement>(frameElementsCount);

		for (int32_t i = 0; i < frameElementsCount; i++)
		{
			m_frameElements[i].instanceIndex = swf->readUnsignedShort();
			m_frameElements[i].matrixIndex = swf->readUnsignedShort();
			m_frameElements[i].colorTransformIndex = swf->readUnsignedShort();
		}

		uint16_t instancesCount = swf->readUnsignedShort();
		m_instances = std::vector<DisplayObjectInstance>(instancesCount);

		for (int16_t i = 0; i < instancesCount; i++)
		{
			m_instances[i].id = swf->readUnsignedShort();
		}

		if (tag == 12 || tag == 35)
		{
			for (int16_t i = 0; i < instancesCount; i++)
			{
				m_instances[i].blend = swf->readUnsignedByte();
			}
		}

		for (int16_t i = 0; i < instancesCount; i++)
		{
			m_instances[i].name = swf->readAscii();
		}

		uint16_t framesLoaded = 0;
		while (true)
		{
			uint8_t frameTag = swf->readUnsignedByte();
			int32_t frameTagLength = swf->readInt();

			if (frameTagLength < 0)
				throw std::runtime_error("Negative frame tag length in .sc file");

			if (frameTag == 0)
				break;

			switch (frameTag)
			{
			case 11:
				m_frames[framesLoaded].load(swf);
				framesLoaded++;
				break;

			case 31:
				m_scalingGrid = new ScalingGrid();
				m_scalingGrid->x = swf->readTwip();
				m_scalingGrid->y = swf->readTwip();
				m_scalingGrid->width = swf->readTwip();
				m_scalingGrid->height = swf->readTwip();
				break;

			case 41:
				m_matrixBankIndex = swf->readUnsignedByte();
				break;

			default:
				swf->skip(frameTagLength);
				break;
			}
		}
	}
}
