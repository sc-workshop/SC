#include "SupercellFlash/SupercellSWF.h"
#include "SupercellFlash/tag/TextField.h"

namespace sc
{
	void TextField::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();

		m_fontName = swf->readFontName();
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
			m_bendAngle = swf->readShort() * 91.019f;

		if (tag > 43)
			m_autoAdjustFontBounds = swf->readBool();
	}

	void TextField::save(SupercellSWF* swf)
	{
		/* Writer init */

		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		/* Tag processing */

		uint8_t tag = 7;

		// TODO: other tags, I am too lazy again

		/* Writing */
		tagStream.writeUInt16(m_id);

		tagStream.writeUInt8(m_fontName.length());

		// FIXME: I think we should rework some methods in ByteStream
		const char* c_fontName = m_fontName.c_str();
		tagStream.write(&c_fontName, m_fontName.length());

		tagStream.writeInt32(m_fontColor);

		// We dont't have writeBool at ByteStream wtf
		tagStream.writeUInt8(m_isBold);
		tagStream.writeUInt8(m_isItalic);
		tagStream.writeUInt8(m_isMultiline);
		tagStream.writeUInt8(0); // unused

		tagStream.writeUInt8(m_fontAlign);
		tagStream.writeUInt8(m_fontSize);

		tagStream.writeInt16(m_left);
		tagStream.writeInt16(m_top);
		tagStream.writeInt16(m_right);
		tagStream.writeInt16(m_bottom);

		tagStream.writeUInt8(m_isOutlined);

		// FIXME: kill me please
		const char* c_text = m_text.c_str();
		tagStream.write(&c_text, m_fontName.length());

		// TODO: other tags
	}
}