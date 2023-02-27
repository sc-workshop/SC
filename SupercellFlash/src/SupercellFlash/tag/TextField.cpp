#include "SupercellFlash/SupercellSWF.h"
#include "SupercellFlash/tag/TextField.h"

namespace sc
{
	void TextField::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->stream.readUnsignedShort();

		m_fontName = swf->stream.readAscii();
		m_fontColor = swf->stream.readInt();

		m_isBold = swf->stream.readBool();
		m_isItalic = swf->stream.readBool();
		m_isMultiline = swf->stream.readBool();
		swf->stream.readBool(); // unused

		m_fontAlign = swf->stream.readUnsignedByte();
		m_fontSize = swf->stream.readUnsignedByte();

		m_left = swf->stream.readShort();
		m_top = swf->stream.readShort();
		m_right = swf->stream.readShort();
		m_bottom = swf->stream.readShort();

		m_isOutlined = swf->stream.readBool();

		m_text = swf->stream.readAscii();

		if (tag == TAG_TEXT_FIELD)
			return;

		m_useDeviceFont = swf->stream.readBool();

		if (tag > TAG_TEXT_FIELD_2)
			unknownFlag = (tag != 25);

		if (tag > TAG_TEXT_FIELD_3)
			m_outlineColor = swf->stream.readInt();

		if (tag > TAG_TEXT_FIELD_5)
		{
			unknown1 = swf->stream.readShort();
			unknown2 = swf->stream.readShort();
		}

		if (tag > TAG_TEXT_FIELD_6)
			m_bendAngle = swf->stream.readShort() * 91.019f;

		if (tag > TAG_TEXT_FIELD_7)
			m_autoAdjustFontBounds = swf->stream.readBool();
	}

	void TextField::save(SupercellSWF* swf)
	{
		/* Writer init */

		uint32_t pos = swf->stream.initTag();

		/* Tag processing */

		uint8_t tag = TAG_TEXT_FIELD;

		// TODO: other tags, I am too lazy again

		/* Writing */
		swf->stream.writeUnsignedShort(m_id);

		swf->stream.writeAscii(m_fontName);

		swf->stream.writeInt(m_fontColor);

		swf->stream.writeBool(m_isBold);
		swf->stream.writeBool(m_isItalic);
		swf->stream.writeBool(m_isMultiline);
		swf->stream.writeUnsignedByte(0); // unused

		swf->stream.writeUnsignedByte(m_fontAlign);
		swf->stream.writeUnsignedByte(m_fontSize);

		swf->stream.writeShort(m_left);
		swf->stream.writeShort(m_top);
		swf->stream.writeShort(m_right);
		swf->stream.writeShort(m_bottom);

		swf->stream.writeUnsignedByte(m_isOutlined);

		swf->stream.writeAscii(m_text);

		// TODO: other tags

		swf->stream.finalizeTag(tag, pos);
	}
}
