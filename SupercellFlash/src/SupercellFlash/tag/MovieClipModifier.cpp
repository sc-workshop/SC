#include "MovieClipModifier.h"

#include "SupercellFlash/SupercellSWF.h"

namespace sc {
	void MovieClipModifier::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();

		m_type = (Type)tag;
	}

	void MovieClipModifier::save(SupercellSWF* swf)
	{
		uint8_t tag = (uint8_t)type();

		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		tagStream.writeUInt16(m_id);

		tagStream.close();
		swf->writeTag(tag, tagBuffer);
	}
}