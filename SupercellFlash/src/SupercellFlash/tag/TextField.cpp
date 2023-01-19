#include "SupercellFlash/SupercellSWF.h"
#include "SupercellFlash/tag/TextField.h"

namespace sc
{
	void TextField::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();

		m_fontName = swf->readAscii();
		m_fontColor = swf->readInt();

		m_isBold = swf->readBool();
		m_isItalic = swf->readBool();
		m_isMultiline = swf->readBool();
		swf->readBool(); // unused

		m_fontAlign = swf->readUnsignedByte();
		m_fontSize = swf->readUnsignedByte();

		m_left = swf->readShort();
		m_top = swf->readShort();
		m_right = swf->readShort();
		m_bottom = swf->readShort();

		m_isOutlined = swf->readBool();

		m_text = swf->readAscii();

		if (tag == 7)
			return;

		m_useDeviceFont = swf->readBool();

		if (tag > 15)
			bool flag = (tag != 25);

		if (tag > 20)
			swf->readInt(); // outline color

		if (tag > 25)
		{
			swf->readShort(); // unknown
			swf->readShort(); // unused
		}

		if (tag > 33)
			swf->readShort(); // * 91.91, maybe angle of something

		if (tag > 43)
			m_adjustFontBounds = swf->readBool();
	}
}
