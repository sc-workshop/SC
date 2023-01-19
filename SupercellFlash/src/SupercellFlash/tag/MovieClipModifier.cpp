#include "SupercellFlash/SupercellSWF.h"
#include "MovieClipModifier.h"

namespace sc {
	void MovieClipModifier::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();

		m_type = (Type)tag;
	}
	
	MovieClipModifier::Type MovieClipModifier::getType() { return m_type; }
}