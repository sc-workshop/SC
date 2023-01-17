#include "SupercellSWF.h"
#include "SWFTexture.h"

namespace sc
{
	uint8_t pixelByteSizeTable[] = {
		4,
		4,
		2,
		2,
		2,
		4,
		2,
		4,
		4,
		2,
		1
	};

	void SWFTexture::load(sc::SupercellSWF* swf, uint8_t tag, bool useExternalTexture)
	{
		uint8_t pixelTypeIndex = swf->readUnsignedByte();

		uint16_t m_width = swf->readUnsignedShort();
		uint16_t m_height = swf->readUnsignedShort();

		if (!useExternalTexture)
		{
			// TODO: For now we skipping it, but we should save it as byte array field
			uint8_t pixelByteSize = pixelByteSizeTable[pixelTypeIndex];
			swf->skip(m_width * m_height * pixelByteSize);
		}
	}
}