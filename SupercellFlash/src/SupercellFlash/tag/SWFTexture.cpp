#include "SupercellFlash/SupercellSWF.h"
#include "SupercellFlash/tag/SWFTexture.h"

namespace sc
{
	uint8_t pixelByteSizeTable[] = { 4, 4, 2, 2, 2, 4, 2, 4, 4, 2, 1 };

	void SWFTexture::load(sc::SupercellSWF* swf, uint8_t tag, bool useExternalTexture)
	{
		if (tag == 16 || tag == 19 || tag == 29)
			m_filterIndex = 2;
		else
			m_filterIndex = 1;

		if (tag == 34)
			m_filterIndex = 0;

		m_pixelFormatIndex = swf->readUnsignedByte();

		m_width = swf->readUnsignedShort();
		m_height = swf->readUnsignedShort();

		if (!useExternalTexture)
		{
			uint8_t pixelByteSize = pixelByteSizeTable[m_pixelFormatIndex];
			m_data = swf->read(m_width * m_height * pixelByteSize);
		}
	}
}