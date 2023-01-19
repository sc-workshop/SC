#pragma once

#include "SupercellFlash/common/DisplayObject.h"

namespace sc
{
	class SupercellSWF;

	class TextField : public DisplayObject
	{
	public:
		TextField() { }
		virtual ~TextField() { }

	public:
		void load(SupercellSWF* swf, uint8_t tag);

	private:
		std::string m_text;

		std::string m_fontName;
		int32_t m_fontColor;
		uint8_t m_fontSize;
		uint8_t m_fontAlign;

		int16_t m_left;
		int16_t m_top;
		int16_t m_right;
		int16_t m_bottom;

		bool m_isBold;
		bool m_isItalic;
		bool m_isMultiline;
		bool m_isOutlined;

		bool m_useDeviceFont;
		bool m_adjustFontBounds;
	};
}
